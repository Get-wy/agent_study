'''
Author: 王宇 47047064@qq.com
Date: 2026-04-27 14:29:35
LastEditors: 王宇 47047064@qq.com
LastEditTime: 2026-04-27 15:33:41
FilePath: /AiAgent/deepseek_rag_example.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import os
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Redis
from langchain_classic.text_splitter import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"
DOCUMENT_FILE = Path("alibaba.txt")


def load_env_file(env_path):
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(ENV_FILE)
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not DASHSCOPE_API_KEY:
    raise ValueError(
        f"未找到 DASHSCOPE_API_KEY。请在根目录 env 文件中配置: {ENV_FILE}"
    )


def preview_text(text, limit=120):
    cleaned = text.replace("\n", " ").strip()
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[:limit]}..."


# 1. 初始化阿里 DashScope 聊天模型
# 说明：
# - 这里通过 OpenAI 兼容接口调用阿里通义模型
llm = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# 2. 定义 Prompt 模板
prompt_template = """
请使用以下提供的文本内容来回答问题。仅使用提供的文本信息，
如果文本中没有相关信息，请回答"抱歉，提供的文本中没有这个信息"。

文本内容：{context}
问题：{question}
回答：
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"],
)


# 3. 初始化 Embedding 模型
# 这里继续使用阿里 DashScope 的向量模型
embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=DASHSCOPE_API_KEY,
)


# 4. 加载本地文本文件
if not DOCUMENT_FILE.exists():
    raise FileNotFoundError(
        f"未找到文档文件: {DOCUMENT_FILE.resolve()}。请在执行目录下放置 alibaba.txt，或切换到包含该文件的目录后再运行。"
    )

loader = TextLoader(str(DOCUMENT_FILE), encoding="utf-8")
documents = loader.load()
print("\n=== 第 1 步：加载文档 ===")
print(f"文档数量: {len(documents)}")
if documents:
    print(f"首个文档预览: {preview_text(documents[0].page_content)}")


# 5. 文档切分
text_splitter = CharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
)
texts = text_splitter.split_documents(documents)
print("\n=== 第 2 步：切分文档 ===")
print(f"切分后 chunk 数量: {len(texts)}")
if texts:
    print(f"第 1 个 chunk 长度: {len(texts[0].page_content)}")
    print(f"第 1 个 chunk 预览: {preview_text(texts[0].page_content)}")


# 6. 构建 Redis 向量库
vector_store = Redis.from_documents(
    documents=texts,
    embedding=embeddings,
    redis_url="redis://localhost:6379",
    index_name="dashscope_rag_index",
)
print("\n=== 第 3 步：写入向量库 ===")
print("向量库类型: Redis")
print("索引名: dashscope_rag_index")
print("Embedding 模型: text-embedding-v3")


# 7. 创建检索器
retriever = vector_store.as_retriever(search_kwargs={"k": 2})
print("\n=== 第 4 步：创建检索器 ===")
print("检索参数: k=2")


# 8. 把检索结果拼成上下文字符串
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# 9. 组装 RAG Chain
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
)


# 10. 发起提问
QUESTION = input("\n请输入你的问题: ").strip()
if not QUESTION:
    raise ValueError("问题不能为空，请重新运行后输入问题。")

print("\n=== 第 5 步：先检索，再交给大模型 ===")
retrieved_docs = retriever.invoke(QUESTION)

for index, doc in enumerate(retrieved_docs, start=1):
    print(f"检索结果 {index}: {preview_text(doc.page_content)}")

context = format_docs(retrieved_docs)

print("\n=== 第 6 步：调用大模型生成答案 ===")
result = rag_chain.invoke(QUESTION)
print(f"返回对象类型: {type(result).__name__}")
print("\n最终回答:")
print(result.content)
