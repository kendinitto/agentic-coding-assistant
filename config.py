import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://172.28.176.1:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3.6-27b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_api_base() -> str:
    if OPENAI_API_KEY:
        return "https://api.openai.com/v1"
    return f"{LLAMA_SERVER_URL}/v1"


def get_model() -> str:
    if OPENAI_API_KEY:
        return "gpt-4o"
    return MODEL_NAME
