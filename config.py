import os
from dotenv import load_dotenv

load_dotenv()

# 大模型配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
MODEL_NAME = "qwen-turbo"

# Redis配置
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "agent.log"