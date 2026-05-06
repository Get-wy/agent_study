import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_llm

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

DB_PATH = Path(__file__).resolve().parent / "sales.db"
llm = get_llm()


# ────────────────────────────────────────────
# 数据库初始化（首次运行创建 mock 数据）
# ────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL
        );
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY, name TEXT, city TEXT, join_date TEXT
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY, customer_id INTEGER, product_id INTEGER,
            quantity INTEGER, total_price REAL, order_date TEXT
        );
    """)
    if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        c.executemany("INSERT INTO products VALUES (?,?,?,?)", [
            (1, "无线键盘",  "外设",   299.0),
            (2, "机械键盘",  "外设",   599.0),
            (3, "4K显示器",  "显示器", 2999.0),
            (4, "27寸显示器","显示器", 1599.0),
            (5, "降噪耳机",  "音频",   899.0),
            (6, "有线鼠标",  "外设",    79.0),
            (7, "无线鼠标",  "外设",   199.0),
            (8, "USB集线器", "配件",   129.0),
            (9, "笔记本支架","配件",   159.0),
            (10,"网络摄像头","视频",   399.0),
        ])
        c.executemany("INSERT INTO customers VALUES (?,?,?,?)", [
            (1, "张三",  "北京", "2024-01-15"),
            (2, "李四",  "上海", "2024-02-20"),
            (3, "王五",  "广州", "2024-03-10"),
            (4, "赵六",  "北京", "2024-03-25"),
            (5, "孙七",  "深圳", "2024-04-05"),
            (6, "周八",  "上海", "2024-04-18"),
            (7, "吴九",  "杭州", "2024-05-01"),
            (8, "郑十",  "北京", "2024-05-15"),
            (9, "冯十一","成都", "2024-06-01"),
            (10,"陈十二","上海", "2024-06-20"),
        ])
        c.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", [
            (1,  1, 3, 1, 2999.0, "2024-04-01"),
            (2,  2, 1, 2,  598.0, "2024-04-05"),
            (3,  1, 5, 1,  899.0, "2024-04-10"),
            (4,  3, 2, 1,  599.0, "2024-04-15"),
            (5,  4, 6, 3,  237.0, "2024-04-20"),
            (6,  2, 3, 1, 2999.0, "2024-04-22"),
            (7,  5, 7, 1,  199.0, "2024-04-25"),
            (8,  1, 8, 2,  258.0, "2024-04-28"),
            (9,  6, 5, 1,  899.0, "2024-05-01"),
            (10, 3, 4, 1, 1599.0, "2024-05-05"),
            (11, 7, 9, 2,  318.0, "2024-05-08"),
            (12, 4,10, 1,  399.0, "2024-05-10"),
            (13, 8, 2, 1,  599.0, "2024-05-12"),
            (14, 2, 7, 1,  199.0, "2024-05-15"),
            (15, 9, 1, 1,  299.0, "2024-05-18"),
            (16,10, 3, 1, 2999.0, "2024-05-20"),
            (17, 5, 4, 1, 1599.0, "2024-05-22"),
            (18, 1, 6, 2,  158.0, "2024-05-25"),
            (19, 6, 8, 1,  129.0, "2024-05-28"),
            (20, 3, 5, 1,  899.0, "2024-05-30"),
        ])
    conn.commit()
    conn.close()
    print(f"数据库就绪: {DB_PATH}")


# ────────────────────────────────────────────
# 工具定义
# ────────────────────────────────────────────
@tool
def get_schema() -> str:
    """获取数据库所有表的字段结构，生成 SQL 前必须先调用此工具"""
    return """
数据库包含3张表：

products(id, name, category, price)
  - category 取值：外设 / 显示器 / 音频 / 配件 / 视频
  - price：单价（元）

customers(id, name, city, join_date)
  - join_date：格式 YYYY-MM-DD

orders(id, customer_id, product_id, quantity, total_price, order_date)
  - customer_id → customers.id
  - product_id  → products.id
  - total_price：订单总金额（元）
  - order_date：格式 YYYY-MM-DD
"""


@tool
def execute_sql(query: str) -> str:
    """执行 SQL 查询并返回结果，只允许 SELECT 语句"""
    query = query.strip()
    if not query.upper().startswith("SELECT"):
        return "错误：只允许 SELECT 查询，不允许修改数据"
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        cols = [d[0] for d in c.description]
        conn.close()
        if not rows:
            return "查询结果为空"
        header = " | ".join(cols)
        lines = [header, "-" * len(header)] + [" | ".join(str(v) for v in row) for row in rows]
        return "\n".join(lines)
    except Exception as e:
        return f"SQL 执行错误: {e}"


tools = [get_schema, execute_sql]

REACT_TEMPLATE = """你是一个数据分析助手，帮助用户查询销售数据库。

可用工具：
{tools}

必须严格按照以下格式（关键词不变）：

Question: 用户的问题
Thought: 思考下一步
Action: 工具名，必须是 [{tool_names}] 之一
Action Input: 传给工具的参数
Observation: 工具返回的结果
...（可重复）
Thought: 我现在知道最终答案了
Final Answer: 用自然语言解释查询结果，给出洞察

开始！

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(REACT_TEMPLATE)
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=8,
    handle_parsing_errors=True,
)

SAMPLE_QUESTIONS = [
    "销售额最高的产品是哪个？",
    "购买过3次及以上的客户有哪些？",
    "每个城市的总销售额是多少？按从高到低排序",
]


def run_query(question: str):
    print(f"\n{'=' * 55}")
    print(f"问题: {question}")
    print("=" * 55)
    result = agent_executor.invoke({"input": question})
    print(f"\n最终回答: {result['output']}")


if __name__ == "__main__":
    init_db()

    # Demo 1: 示例查询（展示 Agent 完整推理过程）
    print("\n【示例查询】")
    for q in SAMPLE_QUESTIONS:
        run_query(q)

    # Demo 2: 交互模式
    print("\n【交互模式 —— 输入 quit 退出】")
    while True:
        q = input("\n你的问题: ").strip()
        if q.lower() in ("quit", "exit", "q", "退出"):
            break
        if q:
            run_query(q)
