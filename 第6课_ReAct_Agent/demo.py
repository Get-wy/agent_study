import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_llm

from langchain.agents import create_agent as create_react_agent
from langchain_core.tools import tool

# 安装：langgraph（langchain 1.x 已内置 langgraph 依赖）

llm = get_llm()


@tool
def search_weather(city: str) -> str:
    """查询指定城市的今日天气，支持北京、上海、广州"""
    mock_data = {
        "北京": "晴天，气温 22°C，湿度 40%，微风",
        "上海": "多云，气温 28°C，湿度 75%，东南风3级",
        "广州": "阵雨，气温 30°C，湿度 90%，南风2级",
    }
    return mock_data.get(city, f"{city}：暂无数据（支持：北京、上海、广州）")


@tool
def calculate(expr: str) -> str:
    """计算数学表达式，例如 '100 * 7.25' 或 '22 + 100'"""
    try:
        result = eval(expr, {"__builtins__": {}}, {})
        return f"{expr} = {result}"
    except Exception as e:
        return f"计算失败: {e}"


@tool
def get_exchange_rate(currency: str) -> str:
    """查询1单位外币兑换人民币的汇率，支持 USD、EUR、JPY"""
    rates = {"USD": 7.25, "EUR": 7.89, "JPY": 0.048}
    rate = rates.get(currency.upper())
    if rate is None:
        return f"不支持 {currency}，可用：USD、EUR、JPY"
    return f"1 {currency} = {rate} CNY"


tools = [search_weather, calculate, get_exchange_rate]

# LangGraph 的 create_react_agent：自动处理 Thought→Action→Observation 循环
agent = create_react_agent(llm, tools)


def run(question: str, label: str):
    print(f"\n{'=' * 55}")
    print(f"{label}")
    print(f"{'=' * 55}")
    print(f"用户: {question}")

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    
    # 打印中间推理步骤
    for msg in result["messages"]:
        role = getattr(msg, "type", type(msg).__name__)
        if role == "tool":
            print(f"  [工具返回] {msg.content}")
        elif role == "ai" and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  [调用工具] {tc['name']}({tc['args']})")

    final = result["messages"][-1].content
    print(f"\n最终回答: {final}")


if __name__ == "__main__":
    # Demo 1: 单步任务，LLM 调一个工具即可回答
    # run("北京今天天气怎么样？", "Demo 1: 单步任务")

    # Demo 2: 多步任务，LLM 自主决定调哪些工具、按什么顺序
    run(
        "北京今天气温多少度？100美元能换多少人民币？把这两个数字加起来。",
        "Demo 2: 多步任务（观察 Agent 自主规划工具顺序）",
    )
