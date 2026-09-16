from typing import List, Dict

def clean_messages(messages: List[Dict]) -> List[Dict]:
    """清洗消息字典，剔除值为None的字段"""
    res = []
    for msg in messages:
        new_msg = {k: v for k, v in msg.items() if v is not None}
        res.append(new_msg)
    return res


def trim_chat_history(system_msg: Dict, chat_history: List[Dict], max_len: int):
    """截断对话历史，保留system，取后面max_len-1条"""
    new_history = [system_msg] + chat_history[-(max_len - 1):]
    return new_history