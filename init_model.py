from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
import dashscope

import config

# ===== 全局配置 =====
dashscope.api_key = config.API_KEY

# ===== 文本大模型 =====
Text_llm = ChatOpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL,
    model=config.TEXT_MODEL, 
)

# ===== 嵌入大模型 =====
Embeddings = DashScopeEmbeddings(
    model=config.EMBEDDING_MODEL_PATH,
)
