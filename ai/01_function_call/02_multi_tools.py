"""
模块 3 示例：多工具协作（搜索、计算器、日期）+ 工具调用链

演示：同一对话中模型自动选工具；可先 search 再 calculate，形成链式调用。
"""

from __future__ import annotations

import ast
import json
import operator
import os
from datetime import date, datetime
from typing import Any, Callable

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------- 模拟数据：搜索库 ----------
_SEARCH_INDEX: list[dict[str, str]] = [
    {
        "title": "Python 3.12 新特性",
        "snippet": "Python 3.12 于 2023-10-02 发布，包含改进的错误消息、f-string 等。",
    },
    {
        "title": "Harness Engineering 简介",
        "snippet": "Harness Engineering 关注 Agent 在生产环境中的可靠性、可观测性与成本控制。",
    },
    {
        "title": "北京气候概览",
        "snippet": "北京年均气温约 12°C，夏季多雨，冬季干燥。示例检索句：去年夏至是 6 月 21 日。",
    },
]


def mock_search(query: str, top_k: int = 2) -> dict[str, Any]:
    """简单关键词匹配模拟搜索。"""
    q = query.strip().lower()
    scored: list[tuple[int, dict[str, str]]] = []
    for doc in _SEARCH_INDEX:
        text = (doc["title"] + " " + doc["snippet"]).lower()
        score = sum(1 for w in q.split() if len(w) > 1 and w in text)
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    hits = [d for s, d in scored if s > 0][: max(1, min(top_k, 5))]
    if not hits:
        hits = scored[:1][0][1]  # 至少返回一条弱相关
        hits = [hits] if isinstance(hits, dict) else hits
    return {"query": query, "results": hits}


# ---------- 安全算术（仅允许数字与 + - * / 一元负号）----------
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _eval_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_ast(node.operand)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        return float(_ALLOWED_BINOPS[type(node.op)](left, right))
    raise ValueError("不支持的表达式")


def safe_calculate(expression: str) -> dict[str, Any]:
    """计算四则运算表达式，禁止变量与函数调用。"""
    expr = expression.strip()
    if not expr:
        return {"error": "表达式为空"}
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        return {"error": f"语法错误: {e}"}
    if not isinstance(tree.body, ast.Expression):
        return {"error": "仅支持单表达式"}
    try:
        value = _eval_ast(tree.body.value)
    except Exception as e:
        return {"error": str(e)}
    return {"expression": expr, "value": value}


def query_date_info(kind: str, ref: str | None = None) -> dict[str, Any]:
    """
    kind: 'today' | 'weekday' | 'parse'
    ref: 当 kind 为 parse 时，传入 YYYY-MM-DD
    """
    k = kind.strip().lower()
    today = date.today()
    if k == "today":
        return {"iso_date": today.isoformat(), "weekday": today.strftime("%A")}
    if k == "weekday":
        return {"iso_date": today.isoformat(), "weekday_cn": "一二三四五六日"[today.weekday()]}
    if k == "parse" and ref:
        try:
            d = datetime.strptime(ref.strip(), "%Y-%m-%d").date()
        except ValueError:
            return {"error": "日期格式应为 YYYY-MM-DD"}
        return {"iso_date": d.isoformat(), "weekday_cn": "一二三四五六日"[d.weekday()]}
    return {"error": "未知 kind 或缺少 ref"}


# ---------- 工具注册表：名称 -> 函数 ----------
ToolFn = Callable[..., dict[str, Any]]

TOOL_REGISTRY: dict[str, ToolFn] = {
    "mock_search": mock_search,
    "safe_calculate": safe_calculate,
    "query_date_info": query_date_info,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "mock_search",
            "description": "在小型模拟知识库中做关键词搜索。用户需要背景资料、事实检索、文档片段时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词或短语"},
                    "top_k": {
                        "type": "integer",
                        "description": "返回条数，默认 2，最大 5",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "safe_calculate",
            "description": "对仅含数字与 + - * / 的算术表达式求值。需要数值运算、加减乘除时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "算术表达式，如 (12 + 3) * 4",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_date_info",
            "description": "查询今天日期、星期，或解析某日的星期。涉及日期、星期几时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "kind": {
                        "type": "string",
                        "enum": ["today", "weekday", "parse"],
                        "description": "today=今天；weekday=今天星期；parse=解析 ref 日期",
                    },
                    "ref": {
                        "type": "string",
                        "description": "kind=parse 时必填，格式 YYYY-MM-DD",
                    },
                },
                "required": ["kind"],
            },
        },
    },
]


def dispatch_tool(name: str, arguments_json: str) -> str:
    fn = TOOL_REGISTRY.get(name)
    if not fn:
        return json.dumps({"error": f"未注册工具: {name}"}, ensure_ascii=False)
    try:
        args = json.loads(arguments_json) if arguments_json else {}
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"JSON 解析失败: {e}"}, ensure_ascii=False)
    try:
        out = fn(**args)
    except TypeError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    return json.dumps(out, ensure_ascii=False)


def chat_with_tools(
    client: OpenAI,
    model: str,
    messages: list[dict[str, Any]],
    max_tool_rounds: int = 6,
) -> str:
    """
    多轮工具循环：直到没有 tool_calls 或达到轮次上限。
    工具调用链：上一轮 tool 输出在 messages 中，模型可在下一轮再次发起 tool_calls。
    """
    rounds = 0
    while rounds < max_tool_rounds:
        rounds += 1
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump())

        if not msg.tool_calls:
            return msg.content or ""

        for tc in msg.tool_calls:
            out = dispatch_tool(tc.function.name, tc.function.arguments or "{}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": out,
                }
            )

    return "已达到工具调用轮次上限，请缩短任务或检查提示。"


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("请在 .env 中设置 OPENAI_API_KEY")

    client_kwargs: dict = {"api_key": api_key}
    if os.getenv("OPENAI_BASE_URL"):
        client_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(**client_kwargs)
    model = os.getenv("OPENAI_MODEL", "glm-4-flash")

    # 意图：先检索 Python 3.12 发布相关信息，再基于 snippet 中的年份做简单计算（演示链）
    user_text = (
        "先搜索 Python 3.12 相关介绍，然后根据你看到的发布年份，"
        "计算 2026 减去该年份等于多少（用计算器工具算）。"
    )

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "你是严谨的助手。需要事实时先用 mock_search；需要算数时用 safe_calculate；"
                "需要日期星期时用 query_date_info。不要编造搜索库中没有的细节。"
            ),
        },
        {"role": "user", "content": user_text},
    ]

    answer = chat_with_tools(client, model, messages)
    print("--- 用户 ---")
    print(user_text)
    print("\n--- 助手回复 ---")
    print(answer)


if __name__ == "__main__":
    main()
