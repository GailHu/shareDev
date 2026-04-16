"""
模块 4 示例：对话短期记忆与按 Token 滑动窗口。
依赖：tiktoken、openai、python-dotenv（可选，用于读取 OPENAI_API_KEY）。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Literal

import tiktoken
from dotenv import load_dotenv

load_dotenv()

Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    """单条对话消息。"""

    role: Role
    content: str


class ConversationMemory:
    """
    对话记忆：消息列表 + 按总 Token 上限滑动窗口。
    优先保留 system（若存在），从最早的用户/助手消息开始丢弃。
    """

    def __init__(
        self,
        max_tokens: int = 3000,
        encoding_name: str = "cl100k_base",
    ) -> None:
        self._messages: List[Message] = []
        self.max_tokens = max_tokens
        self._encoding = tiktoken.get_encoding(encoding_name)

    def count_text_tokens(self, text: str) -> int:
        """计算单段文本的 Token 数。"""
        return len(self._encoding.encode(text))

    def _message_tokens(self, m: Message) -> int:
        # OpenAI 消息格式约 4 tokens/条开销（文档惯例估算）
        overhead = 4
        return overhead + self.count_text_tokens(m.content)

    def total_tokens(self) -> int:
        """当前列表估算总 Token。"""
        return sum(self._message_tokens(m) for m in self._messages)

    def add_message(self, role: Role, content: str) -> None:
        """追加一条消息并应用滑动窗口。"""
        self._messages.append(Message(role=role, content=content))
        self._apply_sliding_window()

    def _apply_sliding_window(self) -> None:
        """超过 max_tokens 时从旧到新删除，尽量保留首条 system。"""
        if self.total_tokens() <= self.max_tokens:
            return

        system_kept: List[Message] = []
        rest: List[Message] = []
        if self._messages and self._messages[0].role == "system":
            system_kept = [self._messages[0]]
            rest = self._messages[1:]
        else:
            rest = list(self._messages)

        # 至少保留最后一条（刚加入的）
        while rest and self._total_with(system_kept + rest) > self.max_tokens:
            if len(rest) <= 1:
                break
            rest.pop(0)

        self._messages = system_kept + rest

        # 若仍超限（例如单条极长），仅保留最后一条
        while self.total_tokens() > self.max_tokens and len(self._messages) > 1:
            if self._messages[0].role == "system":
                if len(self._messages) <= 2:
                    break
                self._messages.pop(1)
            else:
                self._messages.pop(0)

    def _total_with(self, msgs: List[Message]) -> int:
        return sum(self._message_tokens(m) for m in msgs)

    def get_recent(self, n: int) -> List[Message]:
        """返回最近 n 条消息（不足则全部返回）。"""
        if n <= 0:
            return []
        return self._messages[-n:]

    def get_messages_for_api(self) -> List[dict]:
        """转为 Chat Completions 所需的 message 字典列表。"""
        return [{"role": m.role, "content": m.content} for m in self._messages]

    def clear(self) -> None:
        self._messages.clear()


def run_simple_agent() -> None:
    """简单 CLI 对话：带短期记忆，可选调用 OpenAI。"""
    api_key = os.getenv("OPENAI_API_KEY")
    system_prompt = (
        "你是一个简洁、有帮助的中文助手。根据对话历史回答用户。"
    )
    memory = ConversationMemory(max_tokens=2500)
    memory.add_message("system", system_prompt)

    print("=== 对话记忆示例（输入 quit 退出）===")
    if not api_key:
        print("未设置 OPENAI_API_KEY，将仅演示记忆结构与 Token 计数。\n")

    client = None
    try:
        from openai import OpenAI

        if api_key:
            client_kwargs: dict = {"api_key": api_key}
            if os.getenv("OPENAI_BASE_URL"):
                client_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
            client = OpenAI(**client_kwargs)
    except Exception:
        client = None

    while True:
        user = input("\n用户: ").strip()
        if user.lower() in ("quit", "exit", "q"):
            break
        memory.add_message("user", user)

        messages = memory.get_messages_for_api()
        if client:
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "glm-4-flash"),
                messages=messages,
                temperature=0.7,
            )
            reply = resp.choices[0].message.content or ""
        else:
            reply = f"[无 API] 已记录你的消息。当前窗口约 {memory.total_tokens()} tokens。"

        print(f"助手: {reply}")
        memory.add_message("assistant", reply)


if __name__ == "__main__":
    run_simple_agent()
