import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import get_api_key

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Redis
from langchain_classic.text_splitter import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCUMENT_FILE = Path(__file__).resolve().parent.parent / "第1课_最小RAG" / "alibaba.txt"
DASHSCOPE_API_KEY = get_api_key()
TEST_QUESTION = "智核科技的员工晋升有哪些？"

embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=DASHSCOPE_API_KEY,
)


def load_docs():
    loader = TextLoader(str(DOCUMENT_FILE), encoding="utf-8")
    return loader.load()


def build_store(splitter, index_name: str):
    docs = load_docs()
    chunks = splitter.split_documents(docs)
    store = Redis.from_documents(
        documents=chunks,
        embedding=embeddings,
        redis_url="redis://localhost:6379",
        index_name=index_name,
    )
    return store, chunks


def show_results(store, k: int, label: str):
    retriever = store.as_retriever(search_kwargs={"k": k})
    results = retriever.invoke(TEST_QUESTION)
    print(f"\n  {label} | k={k} | 检索到 {len(results)} 条")
    for i, doc in enumerate(results, 1):
        preview = doc.page_content[:80].replace("\n", " ")
        print(f"  [{i}] ({len(doc.page_content)}字) {preview}...")


# ────────────────────────────────────────────
# Demo 1: Splitter 类型对比
# CharacterTextSplitter 按固定字符切；RecursiveCharacterTextSplitter 优先按段落/句子切
# ────────────────────────────────────────────
def demo_splitter_comparison():
    print("\n" + "=" * 55)
    print("Demo 1: Splitter 类型对比")
    print(f"问题: {TEST_QUESTION}")
    print("=" * 55)

    char_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20, separator="\n")
    char_store, char_chunks = build_store(char_splitter, "rag5_char")
    print(f"\nCharacterTextSplitter: 切出 {len(char_chunks)} 个 chunk")
    show_results(char_store, k=3, label="CharacterTextSplitter")

    rec_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    rec_store, rec_chunks = build_store(rec_splitter, "rag5_recursive")
    print(f"\nRecursiveCharacterTextSplitter: 切出 {len(rec_chunks)} 个 chunk")
    show_results(rec_store, k=3, label="RecursiveCharacterTextSplitter")


# ────────────────────────────────────────────
# Demo 2: chunk_size 调优
# 同一文档，chunk_size 越小切得越碎，越大信息越完整但噪音也越多
# ────────────────────────────────────────────
def demo_chunk_size():
    print("\n" + "=" * 55)
    print("Demo 2: chunk_size 调优")
    print(f"问题: {TEST_QUESTION}")
    print("=" * 55)

    for chunk_size, overlap in [(200, 40), (400, 80), (800, 160)]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        store, chunks = build_store(splitter, f"rag5_size{chunk_size}")
        print(f"\nchunk_size={chunk_size}, overlap={overlap}: 共 {len(chunks)} 个 chunk")
        show_results(store, k=3, label=f"size={chunk_size}")


# ────────────────────────────────────────────
# Demo 3: k 值调整
# k 越大召回越多，但噪音也越多；k 越小精度高，但可能漏掉关键内容
# ────────────────────────────────────────────
def demo_k_value():
    print("\n" + "=" * 55)
    print("Demo 3: k 值调整（chunk_size 固定 500）")
    print(f"问题: {TEST_QUESTION}")
    print("=" * 55)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    store, _ = build_store(splitter, "rag5_ktest")
    for k in [1, 3, 5]:
        show_results(store, k=k, label=f"k={k}")


if __name__ == "__main__":
    demo_splitter_comparison()
    demo_chunk_size()
    demo_k_value()
