import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_llm

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

llm = get_llm()


# ────────────────────────────────────────────
# 工具定义（全部 mock，无需真实 API）
# ────────────────────────────────────────────
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

# ReAct prompt：LangChain 解析器依赖 Action / Final Answer 这两个英文关键词
REACT_TEMPLATE = """你是一个智能助手，能使用以下工具回答用户问题：

{tools}

必须严格按照以下格式输出（关键词不能改变）：

Question: 用户的问题
Thought: 分析下一步该做什么
Action: 要使用的工具名，必须是 [{tool_names}] 之一
Action Input: 传给工具的参数
Observation: 工具返回的结果
...（上面4行可以重复多次）
Thought: 我现在知道最终答案了
Final Answer: 对用户问题的完整回答

开始！

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(REACT_TEMPLATE)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=6,
    handle_parsing_errors=True,
)


# ────────────────────────────────────────────
# Demo 1: 单步任务
# LLM 决定调一个工具就能回答
# ────────────────────────────────────────────
def demo_single_step():
    print("\n" + "=" * 55)
    print("Demo 1: 单步任务")
    print("=" * 55)
    result = agent_executor.invoke({"input": "北京今天天气怎么样？"})
    print(f"\n最终回答: {result['output']}")


# ────────────────────────────────────────────
# Demo 2: 多步任务
# LLM 需要依次调用多个工具，自主规划顺序
# ────────────────────────────────────────────
def demo_multi_step():
    print("\n" + "=" * 55)
    print("Demo 2: 多步任务（观察 Thought→Action→Observation 循环）")
    print("=" * 55)
    result = agent_executor.invoke({
        "input": "北京今天气温多少度？100美元能换多少人民币？把这两个数字加起来。"
    })
    print(f"\n最终回答: {result['output']}")


if __name__ == "__main__":
    demo_single_step()
    demo_multi_step()
