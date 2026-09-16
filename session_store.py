import json
import os
from pathlib import Path
from typing import Dict, Optional
from config import SESSION_DIR

Path(SESSION_DIR).mkdir(exist_ok=True)

def get_session_path(session_id: str) -> Path:
    return Path(SESSION_DIR) / f"{session_id}.json"

async def load_session(session_id: str) -> Optional[Dict]:
    file_path = get_session_path(session_id)
    if not file_path.exists():
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def save_session(session_id: str, data: Dict):
    file_path = get_session_path(session_id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)