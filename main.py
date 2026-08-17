import asyncio
import signal
from typing import List, Dict
from config import MAX_HISTORY_ROUND
from logger_setup import logger
from llm_client import call_llm_with_tool
from tools import run_tool
from session_store import SessionManager

STOP_FLAG = False

def handle_sigint():
    global STOP_FLAG
    STOP_FLAG = True
    logger.warning("检测到Ctrl+C，准备退出")

signal.signal(signal.SIGINT, lambda sig,frame: handle_sigint())

def trim_chat_history(chat_history: List[dict]) -> List[dict]:
    if len(chat_history) <= MAX_HISTORY_ROUND * 2 + 1:
        return chat_history.copy()
    new_history = [chat_history[0]]
    remain = chat_history[1:][-(MAX_HISTORY_ROUND * 2):]
    new_history.extend(remain)
    return new_history


async def main():
    session_mgr = SessionManager()
    sid = session_mgr.create_session_id()
    chat_history = session_mgr.load_history(sid)
    logger.info(f"创建会话:{sid}")
    print("对话启动，输入quit退出")

    while not STOP_FLAG:
        question = input("\n用户：")
        if question.strip().lower() == "quit":
            break
        chat_history.append({"role":"user","content":question})
        chat_history = trim_chat_history(chat_history)

        while True:
            resp_msg = await call_llm_with_tool(chat_history)
            if resp_msg.tool_calls:
                tool_info = resp_msg.tool_calls[0]
                res = run_tool(tool_info)
                # ✅关键修复：ToolCall对象转为字典
                assistant_msg = {
                    "role": "assistant",
                    "content": resp_msg.content,
                    "tool_calls": [item.model_dump() for item in resp_msg.tool_calls]
                }
                chat_history.append(assistant_msg)
                chat_history.append({
                    "role":"tool",
                    "tool_call_id": tool_info.id,
                    "content":res
                })
            else:
                print(f"AI：{resp_msg.content}")
                assistant_msg = {
                    "role": "assistant",
                    "content": resp_msg.content,
                    "tool_calls": [item.model_dump() for item in resp_msg.tool_calls] if resp_msg.tool_calls else None
                }
                chat_history.append(assistant_msg)
                break
        session_mgr.save_history(sid, chat_history)

if __name__ == "__main__":
    asyncio.run(main())