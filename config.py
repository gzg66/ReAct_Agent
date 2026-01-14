import os

# ===== API =====
API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# ===== 默认模型 =====
TEXT_MODEL = "qwen-flash"
VLM_MODEL = "qvq-max"
EMBEDDING_MODEL_PATH = "text-embedding-v4"

