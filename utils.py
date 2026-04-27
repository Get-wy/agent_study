import os
from pathlib import Path
from langchain_community.chat_models.tongyi import ChatTongyi

_ENV_FILE = Path(__file__).resolve().parent / ".env"


def _load_env():
    if not _ENV_FILE.exists():
        return
    for raw_line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_api_key() -> str:
    _load_env()
    key = os.getenv("DASHSCOPE_API_KEY")
    if not key:
        raise ValueError(f"未找到 DASHSCOPE_API_KEY，请在根目录配置: {_ENV_FILE}")
    return key


def get_llm(model: str = "qwen-plus") -> ChatTongyi:
    return ChatTongyi(model=model, dashscope_api_key=get_api_key())
