# 第5-7课设计文档

**日期**: 2026-05-06  
**背景**: 基于已完成的第1-4课，继续完善 AI Agent 学习路线图的后续课程

---

## 第5课：RAG 质量调优

### 目标
让学员理解 RAG 检索质量的关键参数，通过对比实验建立直觉。

### 技术选型
- 向量库：Redis（沿用第1课，无需新安装）
- 文档：阿里巴巴公司介绍（第1课已有 `alibaba.txt`）
- 框架：LangChain

### Demo 结构

**Demo 1 — Splitter 对比**
- `CharacterTextSplitter`（按固定字符数切）vs `RecursiveCharacterTextSplitter`（递归按段落/句子切）
- 同一问题，打印两种切分方式检索到的 chunk 内容，肉眼对比边界质量

**Demo 2 — chunk_size 调优**
- chunk_size = 200 / 500 / 1000，chunk_overlap 固定为 chunk_size 的 20%（分别为 40 / 100 / 200）
- 打印各档次下检索结果的长度与内容完整性

**Demo 3 — k 值调整**
- k = 1 / 3 / 5，chunk_size 固定 500
- 打印召回数量与噪音，理解精确率与召回率的权衡

### 新增依赖
无

---

## 第6课：ReAct Agent

### 目标
理解 ReAct（Reason + Act）模式，看懂 LLM 如何自主规划和执行多步任务。

### 技术选型
- `langchain` 的 `create_react_agent` + `AgentExecutor`
- 全部使用 mock 工具，无需真实 API

### 工具定义

| 工具 | 输入 | 输出 | 说明 |
|------|------|------|------|
| `search_weather(city)` | 城市名 | mock 天气字符串 | 固定返回，演示用 |
| `calculate(expr)` | 数学表达式字符串 | 计算结果 | `eval` 实现 |
| `get_exchange_rate(from_currency)` | 货币代码 | mock 汇率 | 固定返回，演示用 |

### Demo 结构

**Demo 1 — 单步任务**
- 问题："北京今天天气怎么样？"
- 预期过程：Thought → Action(search_weather) → Observation → 最终回答

**Demo 2 — 多步任务**
- 问题："北京今天气温多少度？100美元能换多少人民币？把两个结果加起来告诉我"
- 预期过程：多轮 Thought→Action→Observation，展示自主规划能力

- 两个 Demo 均开启 `verbose=True`，完整展示推理链

### 新增依赖
无（`langchain` 已安装）

---

## 第7课：AI 数据查询助手（综合 Demo）

### 目标
整合 Function Calling + ReAct Agent，实现自然语言驱动的数据库查询，可作为面试项目素材。

### 技术选型
- 数据库：SQLite（Python 内置，零配置）
- Agent：复用第6课的 `create_react_agent` + `AgentExecutor`
- 无需额外依赖

### 数据库设计

```sql
-- products: 产品表（10条 mock 数据）
id, name, category, price

-- customers: 客户表（10条 mock 数据）
id, name, city, join_date

-- orders: 订单表（20条 mock 数据）
id, customer_id, product_id, quantity, total_price, order_date
```

### 工具定义

| 工具 | 功能 |
|------|------|
| `get_schema()` | 返回所有表的建表语句，供 LLM 了解数据结构 |
| `execute_sql(query)` | 执行只读 SQL（SELECT only，防止误写），返回结果字符串 |

### Demo 结构

**Demo 1 — 初始化数据库**（仅首次运行）

**Demo 2 — 单次查询**
- 问题："销售额最高的产品是哪个？"
- 预期过程：get_schema → 生成SQL → execute_sql → 解释结果

**Demo 3 — 命令行交互**
- 用户循环输入问题，Agent 自主回答
- 示例问题预置：
  - "最近30天哪个城市下单最多？"
  - "购买过3次以上的客户有哪些？"
  - "每个类别的平均单价是多少？"

### 安全设计
- `execute_sql` 检查 SQL 是否以 `SELECT` 开头，非 SELECT 一律拒绝
- 捕获 SQL 执行异常，返回友好错误提示给 Agent

### 新增依赖
无（sqlite3 为 Python 内置模块）

---

## 文件结构（最终状态）

```
AiAgent/
├── 第5课_RAG质量调优/
│   ├── demo.py
│   └── 基础知识.md
├── 第6课_ReAct_Agent/
│   ├── demo.py
│   └── 基础知识.md
└── 第7课_AI数据查询助手/
    ├── demo.py        # 包含建库逻辑 + Agent 交互
    └── 基础知识.md
```

---

## 面试价值对应

| 课 | 面试问题 |
|----|---------|
| 第5课 | "RAG 效果不好怎么排查和优化？" |
| 第6课 | "Agent 和普通 LLM 调用的区别是什么？" |
| 第7课 | "你做过哪些 AI 相关项目？" |
