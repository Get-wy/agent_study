import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_llm

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = get_llm()


# ────────────────────────────────────────────
# Demo 1: 全量记忆
# 把所有历史消息都拼进每次请求，LLM 能记住一切，但 token 线性增长
# ────────────────────────────────────────────
def demo_full_history():
    print("\n=== Demo 1: 全量记忆 ===")
    messages = []

    turns = [
        "我叫小明，我是一名前端工程师",
        "我在学 AI Agent，已经学完了 Function Calling 和 Streaming",
        "我叫什么名字？我学了什么？",  # 测试记忆
    ]

    for user_input in turns:
        print(f"\n用户: {user_input}")
        messages.append(HumanMessage(user_input))

        response = llm.invoke(messages)
        ai_reply = response.content
        messages.append(AIMessage(ai_reply))

        total_chars = sum(len(m.content) for m in messages)
        print(f"AI: {ai_reply}")
        print(f"  [消息数: {len(messages)}, 累计字符: {total_chars}]")


# ────────────────────────────────────────────
# Demo 2: 窗口记忆
# 只保留最近 max_turns 轮，早期对话会被丢弃
# ────────────────────────────────────────────
def demo_window_memory(max_turns: int = 2):
    print(f"\n=== Demo 2: 窗口记忆（保留最近 {max_turns} 轮）===")
    history = []  # [(human_text, ai_text), ...]

    turns = [
        "我叫小明",
        "我是前端工程师",
        "我在学 AI Agent",
        "我叫什么名字？",  # 超出窗口，理论上不应该记得
    ]

    for user_input in turns:
        print(f"\n用户: {user_input}")

        recent = history[-max_turns:]
        messages = []
        for human, ai in recent:
            messages.append(HumanMessage(human))
            messages.append(AIMessage(ai))
        messages.append(HumanMessage(user_input))

        response = llm.invoke(messages)
        ai_reply = response.content
        history.append((user_input, ai_reply))

        print(f"AI: {ai_reply}")
        print(f"  [发送消息数: {len(messages)}, 窗口: {len(recent)}/{max_turns} 轮]")


# ────────────────────────────────────────────
# Demo 3: 摘要记忆
# 近期消息超过阈值就让 LLM 压缩成摘要，再继续对话
# ────────────────────────────────────────────
def _compress(summary: str, messages: list) -> str:
    history_text = "\n".join(
        f"{'用户' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in messages
    )
    prompt = (
        f"请将以下对话压缩成 100 字以内的摘要，保留所有关键信息。\n"
        f"已有摘要：{summary or '无'}\n"
        f"新增对话：\n{history_text}\n"
        f"压缩摘要："
    )
    return llm.invoke([HumanMessage(prompt)]).content


def demo_summary_memory(compress_threshold: int = 4):
    print(f"\n=== Demo 3: 摘要记忆（超过 {compress_threshold} 条触发压缩）===")
    summary = ""
    recent: list = []

    turns = [
        "我叫小明，25 岁",
        "我是前端工程师，在上海工作",
        "我在学 AI Agent，目标是找到更好的工作",
        "我最喜欢的语言是 JavaScript",
        "根据你对我的了解，给我一点学习建议",  # 测试摘要是否保留了信息
    ]

    for user_input in turns:
        print(f"\n用户: {user_input}")

        messages = []
        if summary:
            messages.append(SystemMessage(f"之前对话摘要：\n{summary}"))
        messages.extend(recent)
        messages.append(HumanMessage(user_input))

        response = llm.invoke(messages)
        ai_reply = response.content

        recent.append(HumanMessage(user_input))
        recent.append(AIMessage(ai_reply))

        print(f"AI: {ai_reply}")

        if len(recent) >= compress_threshold:
            print(f"  [触发压缩：{len(recent)} 条消息 → 摘要]")
            summary = _compress(summary, recent)
            recent = []
            print(f"  [摘要：{summary[:60]}...]")


if __name__ == "__main__":
    demo_full_history()
    demo_window_memory()
    demo_summary_memory()
