"""
模块 4 示例：OpenAI Embedding + FAISS 向量记忆，并接入 LLM 对话 Agent。

演示流程（两阶段交互）：
  阶段一「记忆写入」：用户输入若干事实，每条实时编码为向量存入 FAISS
  阶段二「记忆检索」：用户提问，系统检索 Top-K 最相关记忆，注入 Prompt 让 LLM 回答
  每轮对话也自动写回向量库，形成持续增长的长期记忆

持久化机制：
  退出时自动将向量库保存到磁盘（FAISS 索引 + 文本 JSON）
  下次启动时自动加载上次的记忆，实现跨会话长期记忆

支持非交互模式（设置环境变量 NON_INTERACTIVE=1 可自动运行预设演示）

依赖：openai、faiss-cpu、numpy、python-dotenv
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MEMORY_DIR = Path(__file__).parent / "memory_store"
FAISS_INDEX_FILE = "vector_index.faiss"
TEXTS_FILE = "memory_texts.json"


class VectorMemory:
    """最小向量记忆：文本 -> Embedding -> FAISS 内积索引（L2 归一化后等价余弦相似度）。
    支持 save/load 实现跨会话持久化。"""

    def __init__(self, client: OpenAI, embed_model: str = "embedding-3") -> None:
        self._client = client
        self.embed_model = embed_model
        self._texts: List[str] = []
        self._dim: Optional[int] = None
        self._index: Optional[faiss.IndexFlatIP] = None

    def _ensure_index(self, dim: int) -> None:
        if self._index is None:
            self._dim = dim
            self._index = faiss.IndexFlatIP(dim)

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, self._dim or 0)
        r = self._client.embeddings.create(model=self.embed_model, input=texts)
        vecs = np.array([d.embedding for d in r.data], dtype=np.float32)
        faiss.normalize_L2(vecs)
        return vecs

    def add(self, text: str) -> int:
        vec = self._embed_batch([text])
        self._ensure_index(vec.shape[1])
        assert self._index is not None
        self._index.add(vec)
        self._texts.append(text)
        return len(self._texts) - 1

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        if not self._texts or self._index is None or self._index.ntotal == 0:
            return []
        k = min(k, self._index.ntotal)
        q = self._embed_batch([query])
        scores, idxs = self._index.search(q, k)
        out: List[Tuple[str, float]] = []
        for j, sc in zip(idxs[0], scores[0]):
            if 0 <= j < len(self._texts):
                out.append((self._texts[j], float(sc)))
        return out

    @property
    def size(self) -> int:
        return len(self._texts)

    # ── 持久化 ─────────────────────────────────────────────

    def save(self, directory: Path) -> None:
        """将向量索引和文本列表保存到磁盘。"""
        if self._index is None or self._index.ntotal == 0:
            print("  (向量库为空，跳过保存)")
            return

        directory.mkdir(parents=True, exist_ok=True)

        index_path = directory / FAISS_INDEX_FILE
        texts_path = directory / TEXTS_FILE

        faiss.write_index(self._index, str(index_path))

        with open(texts_path, "w", encoding="utf-8") as f:
            json.dump(
                {"embed_model": self.embed_model, "texts": self._texts},
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"  [保存] 向量库已持久化到: {directory}")
        print(f"    - {FAISS_INDEX_FILE} ({index_path.stat().st_size:,} bytes)")
        print(f"    - {TEXTS_FILE} ({len(self._texts)} 条记忆)")

    def load(self, directory: Path) -> bool:
        """从磁盘加载向量索引和文本列表。返回是否成功加载。"""
        index_path = directory / FAISS_INDEX_FILE
        texts_path = directory / TEXTS_FILE

        if not index_path.exists() or not texts_path.exists():
            return False

        try:
            self._index = faiss.read_index(str(index_path))
            self._dim = self._index.d

            with open(texts_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._texts = data.get("texts", [])

            if self._index.ntotal != len(self._texts):
                print(f"  [警告] 索引条数({self._index.ntotal})与文本条数({len(self._texts)})不匹配，重置记忆")
                self._texts = []
                self._index = None
                self._dim = None
                return False

            return True
        except Exception as e:
            print(f"  [警告] 加载记忆失败: {e}，将从空白开始")
            self._texts = []
            self._index = None
            self._dim = None
            return False


# ---------------------------------------------------------------------------


def _load_env() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("请在 .env 中设置 OPENAI_API_KEY")
    kwargs: dict = {"api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _ask_llm(
    client: OpenAI,
    model: str,
    system: str,
    memory_block: str,
    question: str,
    history: List[dict],
) -> Tuple[str, int]:
    messages = [{"role": "system", "content": system}] + history + [
        {
            "role": "user",
            "content": f"【从向量记忆库检索到的相关知识】\n{memory_block}\n\n【用户问题】\n{question}",
        },
    ]
    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=0.3,
    )
    reply = resp.choices[0].message.content or ""
    tokens = getattr(resp.usage, "total_tokens", 0) or 0
    return reply, tokens


def _print_hits(hits: List[Tuple[str, float]]) -> str:
    if not hits:
        print("    （无相关记忆）")
        return "（无相关记忆）"
    for rank, (text, score) in enumerate(hits, 1):
        print(f"    {rank}. [相似度 {score:.4f}] {text}")
    return "\n".join(f"- {t}（相似度 {s:.3f}）" for t, s in hits)


# ---------------------------------------------------------------------------
# 交互模式
# ---------------------------------------------------------------------------


def run_interactive() -> None:
    client = _load_env()
    embed_model = os.getenv("OPENAI_EMBED_MODEL", "embedding-3")
    chat_model = os.getenv("OPENAI_MODEL", "glm-4-flash")
    vm = VectorMemory(client, embed_model=embed_model)

    system_prompt = (
        "你是一个记忆助手。你会收到从向量记忆库中检索到的相关片段，"
        "请优先基于这些检索结果回答用户问题。如果检索结果不足以回答，"
        "请明确说明记忆中没有相关信息。回答保持简洁。"
    )

    print("=" * 60)
    print("  向量记忆 Agent —— 两阶段交互演示")
    print("=" * 60)

    # ── 尝试加载上次保存的记忆 ──────────────────────────────
    loaded = vm.load(MEMORY_DIR)
    if loaded:
        print(f"\n  [加载] 从磁盘恢复了 {vm.size} 条历史记忆")
        print(f"    来源: {MEMORY_DIR}")
        print("  (输入 clear 可清除历史记忆重新开始)")
    else:
        print(f"\n  (未找到历史记忆，从空白开始)")

    # ── 阶段一：记忆写入 ──────────────────────────────────────
    initial_count = vm.size
    print(f"\n[写入] 阶段一：请输入你想让 Agent 记住的事实（每行一条）")
    print("   输入 done 结束写入，进入提问阶段")
    if loaded:
        print("   输入 clear 清除所有历史记忆")
    print()

    new_count = 0
    while True:
        line = input(f"  记忆 [{vm.size + 1}]: ").strip()
        if line.lower() == "clear":
            vm = VectorMemory(client, embed_model=embed_model)
            initial_count = 0
            new_count = 0
            print("  [清除] 已清空所有历史记忆，从空白开始")
            continue
        if line.lower() in ("done", "quit", "exit", "q", ""):
            if vm.size == 0:
                print("  （未输入任何记忆，使用预置示例）")
                for fact in [
                    "我最喜欢的编程语言是 Python",
                    "我的猫叫年糕，今年3岁",
                    "我正在学习 Harness Engineering 课程",
                    "我的生日是 12 月 25 日",
                    "我在北京工作，是一名后端工程师",
                ]:
                    vm.add(fact)
                    new_count += 1
                    print(f"    -> 已存入: {fact}")
            break
        vm.add(line)
        new_count += 1
        print(f"    [OK] 已存入向量库（当前共 {vm.size} 条）")

    print(f"\n  记忆写入完成：历史 {initial_count} 条 + 新增 {new_count} 条 = 共 {vm.size} 条")

    # ── 阶段二：记忆检索问答 ──────────────────────────────────
    print(f"\n{'=' * 60}")
    print("[检索] 阶段二：现在你可以提问，Agent 会从向量记忆中检索并回答")
    print("   输入 quit 退出\n")

    history: List[dict] = []
    total_tokens = 0
    round_num = 0

    while True:
        question = input("  你的问题: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        round_num += 1

        hits = vm.search(question, k=3)
        print(f"\n  [向量检索结果 Top-3]:")
        memory_block = _print_hits(hits)

        reply, tokens = _ask_llm(
            client, chat_model, system_prompt, memory_block, question, history,
        )
        total_tokens += tokens
        print(f"\n  [LLM 回答]（{tokens} tokens）: {reply}\n")

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reply})
        if len(history) > 10:
            history = history[-10:]

        vm.add(f"用户曾问：{question} | 助手曾答：{reply[:150]}")

    # ── 保存记忆到磁盘 ──────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"[统计]")
    print(f"  向量库: {vm.size} 条")
    print(f"  本次新增: {new_count + round_num} 条（写入 {new_count} + 对话 {round_num}）")
    print(f"  问答轮次: {round_num}")
    print(f"  总 Token: {total_tokens}")

    vm.save(MEMORY_DIR)
    print("  下次启动将自动加载这些记忆。再见！")


# ---------------------------------------------------------------------------
# 非交互模式（自动演示）
# ---------------------------------------------------------------------------


def run_non_interactive() -> None:
    client = _load_env()
    embed_model = os.getenv("OPENAI_EMBED_MODEL", "embedding-3")
    chat_model = os.getenv("OPENAI_MODEL", "glm-4-flash")
    vm = VectorMemory(client, embed_model=embed_model)

    system_prompt = (
        "你是一个记忆助手。你会收到从向量记忆库中检索到的相关片段，"
        "请优先基于这些检索结果回答用户问题。如果检索结果不足以回答，"
        "请明确说明记忆中没有相关信息。回答保持简洁，不超过 3 句话。"
    )

    # 尝试加载历史记忆
    loaded = vm.load(MEMORY_DIR)
    if loaded:
        print(f"[加载] 从磁盘恢复了 {vm.size} 条历史记忆\n")

    personal_facts = [
        "我最喜欢的编程语言是 Python，因为它简洁优雅",
        "我的猫叫年糕，是一只橘猫，今年 3 岁",
        "我正在学习 Harness Engineering 课程",
        "我的生日是 12 月 25 日，和圣诞节同一天",
        "我在北京工作，是一名后端工程师",
        "我喜欢用 VS Code 和 Cursor 写代码",
        "上周末我去了故宫",
        "我的手机号尾号是 8888",
    ]

    queries = [
        "我最喜欢什么编程语言？",
        "我的猫叫什么名字？几岁了？",
        "我的生日是哪天？",
        "我在哪个城市工作？做什么的？",
        "上周末我去了哪里？",
    ]

    print("=" * 60)
    print("  向量记忆 Agent —— 自动演示（非交互模式）")
    print("=" * 60)

    # 阶段一
    before_count = vm.size
    print(f"\n[写入] 阶段一：写入 {len(personal_facts)} 条个人事实到向量库")
    print("-" * 40)
    for fact in personal_facts:
        idx = vm.add(fact)
        print(f"  [{idx}] {fact}")
    print(f"  -> 向量库大小: {vm.size} 条（历史 {before_count} + 新增 {len(personal_facts)}）\n")

    # 阶段二
    print(f"[检索] 阶段二：提问关于刚才输入的个人信息")
    print("=" * 60)

    total_tokens = 0
    for qi, question in enumerate(queries, 1):
        print(f"\n{'─' * 60}")
        print(f"问题 {qi}: {question}")

        hits = vm.search(question, k=3)
        print(f"\n  [向量检索结果 Top-3]:")
        memory_block = _print_hits(hits)

        reply, tokens = _ask_llm(
            client, chat_model, system_prompt, memory_block, question, [],
        )
        total_tokens += tokens
        print(f"\n  [LLM 回答]（{tokens} tokens）: {reply}")

        vm.add(f"用户曾问：{question} | 助手曾答：{reply[:150]}")

    # 阶段三
    print(f"\n{'=' * 60}")
    print(f"[统计]:")
    print(f"  初始记忆: {before_count} 条（从磁盘加载）" if loaded else f"  初始记忆: 0 条")
    print(f"  本次写入: {len(personal_facts)} 条事实 + {len(queries)} 条对话")
    print(f"  当前向量库: {vm.size} 条")
    print(f"  总 Token: {total_tokens}")

    print(f"\n  [回溯测试]: \"之前聊了什么？\"")
    hits = vm.search("之前聊了什么？", k=3)
    for rank, (text, score) in enumerate(hits, 1):
        label = "[原始记忆]" if not text.startswith("用户曾问") else "[对话记忆]"
        print(f"    {rank}. {label} [相似度 {score:.4f}] {text[:80]}...")

    # 保存到磁盘
    vm.save(MEMORY_DIR)

    print(f"\n{'=' * 60}")
    print("演示完成。向量记忆实现了：")
    print("  1. 个人事实 -> Embedding -> FAISS 索引存储")
    print("  2. 提问 -> 语义检索出最相关的记忆片段")
    print("  3. 检索结果注入 Prompt -> LLM 据此准确回答")
    print("  4. 对话写回向量库 -> 记忆持续增长")
    print("  5. 退出时保存到磁盘 -> 下次启动自动加载（跨会话记忆）")


# ---------------------------------------------------------------------------


if __name__ == "__main__":
    if os.getenv("NON_INTERACTIVE", "").strip() in ("1", "true", "yes"):
        run_non_interactive()
    else:
        run_interactive()
