# 依赖包记录

## 第1课_最小RAG

```bash
pip install langchain langchain-community langchain-classic langchain-core
```

| 包 | 用途 |
|---|---|
| `langchain` | `init_chat_model` |
| `langchain-community` | `TextLoader`、`DashScopeEmbeddings`、`Redis` 向量库 |
| `langchain-classic` | `CharacterTextSplitter` |
| `langchain-core` | `PromptTemplate`、`RunnablePassthrough` |

> 另需本地运行 Redis 服务

---

## 第2课_Function_Calling

新增包（第1课未安装过）：

```bash
pip install dashscope
```

| 包 | 用途 |
|---|---|
| `dashscope` | `ChatTongyi` 底层驱动，直接调用阿里 DashScope |

---

## 第5-7课

无新增依赖。

| 课 | 用到的包 | 来源 |
|---|---|---|
| 第5课 | `langchain_text_splitters.RecursiveCharacterTextSplitter` | `langchain` 依赖中已包含 |
| 第6课 | `langchain.agents.create_react_agent` / `AgentExecutor` | `langchain` 已安装 |
| 第7课 | `sqlite3` | Python 内置 |
