import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from logger_setup import logger
# 调试打印，确认服务正常启动
print("✅ Server 模块加载成功")

from llm_client import call_llm_with_tool
from tools import run_tool
from exceptions import NetworkRequestError, ParamsInvalidError, ToolExecuteError
from session_store import SessionManager
from main import trim_chat_history

app = FastAPI(title="Agent智能体Web服务")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_manager = SessionManager()

class ChatRequest(BaseModel):
    question: str
    session_id: str

def sse_wrap(text: str):
    return f"data:{text}\n\n"


@app.post("/chat")
async def normal_chat(request: ChatRequest):
    try:
        chat_history = session_manager.load_history(request.session_id)
        chat_history.append({"role": "user", "content": request.question})
        chat_history = trim_chat_history(chat_history)
        answer = ""
        while True:
            resp_msg = await call_llm_with_tool(chat_history)
            if resp_msg.tool_calls:
                tool_call_info = resp_msg.tool_calls[0]
                tool_result = run_tool(tool_call_info)
                assistant_msg = {
                    "role": "assistant",
                    "content": resp_msg.content,
                    "tool_calls": [item.model_dump() for item in resp_msg.tool_calls]
                }
                chat_history.append(assistant_msg)
                chat_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call_info.id,
                    "content": tool_result
                })
            else:
                answer = resp_msg.content
                assistant_msg = {
                    "role": "assistant",
                    "content": resp_msg.content,
                    "tool_calls": [item.model_dump() for item in resp_msg.tool_calls] if resp_msg.tool_calls else None
                }
                chat_history.append(assistant_msg)
                break
        session_manager.save_history(request.session_id, chat_history)
        return {
            "code": 200,
            "msg": "success",
            "data": {"answer": answer}
        }
    except ParamsInvalidError as e:
        logger.warning(f"参数错误：{e}")
        raise HTTPException(status_code=400, detail=f"参数异常:{str(e)}")
    except NetworkRequestError as e:
        logger.error(f"大模型网络异常：{e}")
        raise HTTPException(status_code=503, detail=f"大模型接口访问失败：{str(e)}")
    except ToolExecuteError as e:
        logger.error(f"工具执行失败：{e}")
        raise HTTPException(status_code=500, detail=f"工具调用异常:{str(e)}")
    except Exception as e:
        logger.error(f"服务未知异常", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")


@app.post("/stream_chat")
async def stream_chat(request: ChatRequest):
    async def generate_stream():
        try:
            chat_history = session_manager.load_history(request.session_id)
            chat_history.append({"role": "user", "content": request.question})
            chat_history = trim_chat_history(chat_history)
            while True:
                resp_msg = await call_llm_with_tool(chat_history, stream=False)
                if resp_msg.tool_calls:
                    tool_call_info = resp_msg.tool_calls[0]
                    tool_result = run_tool(tool_call_info)
                    assistant_msg = {
                        "role": "assistant",
                        "content": resp_msg.content,
                        "tool_calls": [item.model_dump() for item in resp_msg.tool_calls]
                    }
                    chat_history.append(assistant_msg)
                    chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call_info.id,
                        "content": tool_result
                    })
                else:
                    for char in resp_msg.content:
                        yield sse_wrap(char)
                        await asyncio.sleep(0.01)
                    assistant_msg = {
                        "role": "assistant",
                        "content": resp_msg.content,
                        "tool_calls": [item.model_dump() for item in resp_msg.tool_calls] if resp_msg.tool_calls else None
                    }
                    chat_history.append(assistant_msg)
                    break
            session_manager.save_history(request.session_id, chat_history)
            yield sse_wrap("[DONE]")
        except Exception as err:
            logger.error(f"流式接口异常: {err}", exc_info=True)
            yield sse_wrap(f"出错：{str(err)}")

    from fastapi.responses import StreamingResponse
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)