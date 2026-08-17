import os
from pathlib import Path

# ========== 临时测试：直接硬编码，绕过.env ==========
DASHSCOPE_API_KEY="sk-ws-H.EEDYEMY.q7Lh.MEYCIQCiuhQZP-WhtdXdsiJiLh0zSBQV8P7gY_mMXh9DE8SQ2AIhAO9BfS9nIkqBdyqXd0xV98xEhvNIo34KfxyjDHJjyYan"
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL="qwen-turbo"
# ==================================================

# 对话配置
MAX_HISTORY_ROUND = 6
# 会话配置
SESSION_DIR = "./sessions"
SESSION_EXPIRE_DAY = 7