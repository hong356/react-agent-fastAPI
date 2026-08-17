import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from config import SESSION_DIR, SESSION_EXPIRE_DAY
from logger_setup import logger

os.makedirs(SESSION_DIR, exist_ok=True)

class SessionManager:
    def __init__(self):
        self.session_dir = SESSION_DIR

    def _get_session_path(self, session_id: str) -> str:
        return os.path.join(self.session_dir, f"{session_id}.json")

    def create_session_id(self) -> str:
        return str(uuid.uuid4())

    def save_history(self, session_id: str, chat_history: List[Dict]):
        path = self._get_session_path(session_id)
        data = {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": chat_history
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话失败: {e}")

    def load_history(self, session_id: str) -> List[Dict]:
        path = self._get_session_path(session_id)
        if not os.path.exists(path):
            return [{"role": "system", "content": "你是智能助手，可以使用工具完成计算。"}]
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("history", [])
        except json.JSONDecodeError:
            logger.warning("会话文件损坏，重置对话")
            return [{"role": "system", "content": "你是智能助手，可以使用工具完成计算。"}]