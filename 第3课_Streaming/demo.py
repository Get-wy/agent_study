import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_llm

from langchain_core.messages import HumanMessage

llm = get_llm()


# ① 基础流式输出：逐字打印
def stream_basic(prompt: str):
    print(f"\n用户: {prompt}")
    print("AI: ", end="", flush=True)

    for chunk in llm.stream([HumanMessage(prompt)]):
        print(chunk.content, end="", flush=True)

    print()


# ② 流式输出 + 收集完整内容（实际项目常用）
def stream_and_collect(prompt: str) -> str:
    print(f"\n用户: {prompt}")
    print("AI: ", end="", flush=True)

    full_content = ""
    for chunk in llm.stream([HumanMessage(prompt)]):
        print(chunk.content, end="", flush=True)
        full_content += chunk.content

    print()
    return full_content


# ③ 模拟 SSE 格式：展示后端真实发给前端的数据长什么样
def stream_as_sse(prompt: str):
    print(f"\n用户: {prompt}")
    print("--- 模拟 SSE 输出（后端 → 前端） ---")

    for chunk in llm.stream([HumanMessage(prompt)]):
        if chunk.content:
            data = json.dumps({"delta": chunk.content}, ensure_ascii=False)
            print(f"data: {data}")

    print("data: [DONE]")


if __name__ == "__main__":
    # 基础演示
    stream_basic("用一句话解释什么是流式输出")

    # 流式 + 收集
    full = stream_and_collect("用三句话介绍 Function Calling")
    print(f"\n[完整内容共 {len(full)} 字]")

    # SSE 格式演示
    stream_as_sse("你好")
