# AiAgent 学习项目

跟着路线图学习 AI Agent 开发，每课一个可运行的 demo。

## 环境准备

```bash
conda activate crs
pip install langchain langchain-community langchain-classic langchain-core dashscope
```

在根目录创建 `.env`：

```
DASHSCOPE_API_KEY=your_key_here
```

## 课程目录

| 课程 | 主题 | 关键知识点 |
|------|------|-----------|
| 第1课 | 最小 RAG | 文档加载 → 向量化 → Redis 检索 → LLM 回答 |
| 第2课 | Function Calling | LLM 自主决策调用工具 |

## 公共工具

`utils.py` 提供两个方法，所有 demo 共用：

- `get_api_key()` — 读取 DashScope API Key
- `get_llm()` — 初始化 qwen-plus 模型
