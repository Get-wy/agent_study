# AiAgent 项目上下文

## 课程目录结构

```
AiAgent/
├── utils.py                    ← 公共工具（env 加载 + LLM 初始化）
├── packages.md                 ← 各课依赖包记录（新包才记，不重复）
├── CLAUDE.md
├── 学习路线图.md
├── 第1课_最小RAG/demo.py
└── 第2课_Function_Calling/demo.py
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

## 环境信息

- conda 环境：`crs`，运行用 `/opt/anaconda3/envs/crs/bin/python`
- 模型：`qwen-plus`（阿里 DashScope）
- 不用 `langchain-openai`（装了也报错，改用 `ChatTongyi`）
