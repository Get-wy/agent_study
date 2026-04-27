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
