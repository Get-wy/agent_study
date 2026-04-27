import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("aliQwen-api"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def get_order_count(date: str) -> dict:
    """模拟查询某天的订单量"""
    fake_data = {
        "2024-01-15": 128,
        "2024-01-16": 97,
        "2024-01-17": 215,
    }
    count = fake_data.get(date, 0)
    return {"date": date, "count": count}


def get_user_info(user_id: str) -> dict:
    """模拟查询用户信息"""
    fake_users = {
        "U001": {"name": "张三", "level": "VIP", "orders": 42},
        "U002": {"name": "李四", "level": "普通", "orders": 3},
    }
    return fake_users.get(user_id, {"error": "用户不存在"})


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_count",
            "description": "查询指定日期的订单量",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "日期，格式 YYYY-MM-DD",
                    }
                },
                "required": ["date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "查询用户的基本信息和订单历史",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "用户ID，格式 U + 数字",
                    }
                },
                "required": ["user_id"],
            },
        },
    },
]

FUNCTION_MAP = {
    "get_order_count": get_order_count,
    "get_user_info": get_user_info,
}


def chat_with_tools(user_message: str):
    print(f"\n用户: {user_message}")
    messages = [{"role": "user", "content": user_message}]

    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        print(f"\n[LLM 决定调用工具]")
        messages.append(msg)

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            print(f"  → 调用: {fn_name}({fn_args})")
            result = FUNCTION_MAP[fn_name](**fn_args)
            print(f"  ← 结果: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        final_response = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
        )
        answer = final_response.choices[0].message.content
    else:
        answer = msg.content

    print(f"\nAI: {answer}")
    return answer


if __name__ == "__main__":
    chat_with_tools("2024-01-17 的订单量是多少？")
    chat_with_tools("帮我查一下用户 U001 的信息")
    chat_with_tools("你好，今天天气怎么样")
