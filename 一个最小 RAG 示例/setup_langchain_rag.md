# LangChain RAG 运行步骤

先创建并进入新的 conda 环境：

```bash
conda create -n langchain-rag python=3.11 -y
conda activate langchain-rag
```

一行安装依赖：

```bash
pip install langchain langchain-community langchain-core langchain-openai langchain-classic docx2txt redis redisvl dashscope
```

运行脚本：

```bash
python /Users/mac/Desktop/AiAgent/deepseek_rag_example.py
```

额外说明：

- 运行前确认本地 Redis 已启动，默认地址是 `redis://localhost:6379`
- 运行前确认 [deepseek_rag_example.py](/Users/mac/Desktop/AiAgent/deepseek_rag_example.py) 顶部已经填了你的 `DASHSCOPE_API_KEY`
- 如果执行时报错，把报错信息发我，我继续帮你定位
