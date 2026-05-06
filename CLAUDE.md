# AiAgent 项目上下文

## 课程目录结构

```
AiAgent/
├── utils.py                    ← 公共工具（env 加载 + LLM 初始化）
├── packages.md                 ← 各课依赖包记录（新包才记，不重复）
├── CLAUDE.md
├── 学习路线图.md
├── 第1课_最小RAG/demo.py
├── 第2课_Function_Calling/demo.py
├── 第3课_Streaming/demo.py
├── 第4课_多轮对话与记忆/demo.py
├── 第5课_RAG质量调优/demo.py
├── 第6课_ReAct_Agent/demo.py
└── 第7课_AI数据查询助手/demo.py
```

## utils.py 公共方法

- `get_api_key()` — 从根目录 `.env` 读取 `DASHSCOPE_API_KEY`，找不到报错
- `get_llm(model="qwen-plus")` — 返回 `ChatTongyi` 实例（langchain_community）

新课 demo 头部固定写法：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_llm, get_api_key
```

## 新课 demo 规范

1. 用 `utils.py` 的公共方法，不要自己写 env 加载或 LLM 初始化
2. demo 基础知识说明里列出本课需要安装的包
3. 新包（之前课程没装过的）追加到根目录 `packages.md`

## 已学课程摘要

### 第1课_最小RAG
- langchain 实现 RAG：加载文档 → 切分 → 向量化 → Redis 存储 → 检索 → LLM 回答
- 依赖：`langchain langchain-community langchain-classic langchain-core`，另需本地 Redis

### 第2课_Function_Calling
- LLM 自主决定调用哪个工具（Function Calling）
- 用 `llm.bind_tools(tools)` 绑定工具，`HumanMessage / ToolMessage` 传递消息
- 依赖新增：`dashscope`

### 第3课_Streaming
- `llm.stream()` 替换 `invoke()`，迭代 chunk 拿分段内容
- SSE 协议：`data: {...}\n\n` + `data: [DONE]\n\n`
- 前端用 `EventSource` 或 `fetch + ReadableStream` 接收
- 无新增依赖

### 第4课_多轮对话与记忆
- LLM 无状态，记忆 = 每次把历史消息列表一起传入
- 三种策略：全量（token线性增长）/ 窗口（保留近N轮）/ 摘要（压缩旧消息）
- `SystemMessage` 设定身份，`HumanMessage / AIMessage` 维护历史
- 持久化：session_id 粒度存 Redis 或数据库
- 无新增依赖

### 第5课_RAG质量调优
- 沿用第1课 Redis + 阿里巴巴文档，对比三个维度的调优效果
- Splitter：`RecursiveCharacterTextSplitter` 优先按段落切，语义比 `CharacterTextSplitter` 更完整
- chunk_size：越小越精确但可能截断长句，越大信息完整但向量语义稀释；从 500 开始调
- k 值：k=3 为默认起点，答案漏掉加大，上下文太长减小
- 无新增依赖

### 第6课_ReAct_Agent
- ReAct = Reason + Act，LLM 自主决定调用哪个工具、按什么顺序、调几次
- `create_react_agent` + `AgentExecutor` 自动处理 Thought→Action→Observation 循环
- `@tool` 装饰器定义工具，docstring 是 LLM 选择工具的依据
- 解析器依赖英文关键词：Action / Action Input / Final Answer，模板里不能改成中文
- `verbose=True` 打印完整推理链，`handle_parsing_errors=True` 防崩溃
- 无新增依赖

### 第7课_AI数据查询助手
- 综合 Demo：自然语言 → get_schema → execute_sql → 自然语言解释
- SQLite 内置，零配置；只允许 SELECT，写操作一律拒绝
- Agent 会自动重试：execute_sql 出错时 Agent 看到错误信息并修正 SQL
- 生产扩展点：换 PostgreSQL 只改连接字符串，加行数限制防超出 context
- 无新增依赖

## 环境信息

- conda 环境：`crs`，运行用 `/opt/anaconda3/envs/crs/bin/python`
- 模型：`qwen-plus`（阿里 DashScope）
- 不用 `langchain-openai`（装了也报错，改用 `ChatTongyi`）
