"""
模块 3 示例：Function Calling 基础（天气查询，模拟数据）

运行前请设置环境变量 OPENAI_API_KEY，或在项目根目录配置 .env。
"""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env（若存在）
load_dotenv()

# ---------- 1. 业务函数（模拟天气） ----------


def get_weather(city: str, unit: str = "celsius") -> dict[str, Any]:
    """模拟天气查询，返回结构化结果。"""
    fake_db = {
        "北京": {"condition": "晴", "temp_c": 22, "humidity": 40},
        "上海": {"condition": "多云", "temp_c": 19, "humidity": 65},
        "guangzhou": {"condition": "阴有小雨", "temp_c": 26, "humidity": 78},
    }
    key = city.strip()
    if key not in fake_db:
        for k in fake_db:
            if k.lower() == key.lower():
                key = k
                break
    data = fake_db.get(key)
    if not data:
        return {"error": f"暂无城市「{city}」的模拟数据", "city": city}
    temp = data["temp_c"]
    if unit == "fahrenheit":
        temp = round(temp * 9 / 5 + 32, 1)
        temp_key = "temp_f"
    else:
        temp_key = "temp_c"
    return {
        "city": key,
        "condition": data["condition"],
        temp_key: temp,
        "humidity": data["humidity"],
        "unit": unit,
    }


# 工具名 -> 可调用对象（本示例仅一个工具）
TOOL_DISPATCH: dict[str, Any] = {
    "get_weather": get_weather,
}


# ---------- 2. OpenAI tools 定义（JSON Schema） ----------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "根据城市名称查询当前天气（教学用模拟数据）。用户问到天气、气温、是否下雨时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，中文或英文，如 北京、上海",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位，默认 celsius（摄氏度）",
                    },
                },
                "required": ["city"],
            },
        },
    }
]


def run_tool_call(name: str, arguments_json: str) -> str:
    """解析参数并执行工具，返回 JSON 字符串供 role=tool 使用。"""
    fn = TOOL_DISPATCH.get(name)
    if not fn:
        return json.dumps({"error": f"未知工具: {name}"}, ensure_ascii=False)
    try:
        args = json.loads(arguments_json) if arguments_json else {}
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"参数 JSON 无效: {e}"}, ensure_ascii=False)
    try:
        result = fn(**args)
    except TypeError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("请在 .env 中设置 OPENAI_API_KEY")

    client_kwargs: dict = {"api_key": api_key}
    if os.getenv("OPENAI_BASE_URL"):
        client_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(**client_kwargs)
    model = os.getenv("OPENAI_MODEL", "glm-4-flash")

    user_text = "帮我查一下上海今天天气怎么样，用摄氏度。"

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": "你是助手。需要天气时调用工具 get_weather，不要编造实时数据。",
        },
        {"role": "user", "content": user_text},
    ]

    # ---------- 3. 第一次请求：模型可能返回 tool_calls ----------
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    msg = response.choices[0].message
    messages.append(msg.model_dump())

    # ---------- 4. 解析 tool_calls，执行函数，写回 tool 消息 ----------
    if msg.tool_calls:
        for tc in msg.tool_calls:
            name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            tool_output = run_tool_call(name, raw_args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_output,
                }
            )

        # ---------- 5. 第二次请求：把工具结果交给模型生成最终回复 ----------
        response2 = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        final = response2.choices[0].message.content
    else:
        final = msg.content

    print("--- 用户 ---")
    print(user_text)
    print("\n--- 助手最终回复 ---")
    print(final or "(无文本内容)")


if __name__ == "__main__":
    main()
