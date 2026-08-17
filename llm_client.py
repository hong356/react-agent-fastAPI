import httpx
import json
import asyncio
from typing import Optional, List
from pydantic import BaseModel
from functools import wraps
from logger_setup import logger
from exceptions import NetworkRequestError
from httpx import TransportError, TimeoutException

# ==========【直接硬编码，不再从config导入】==========
DASHSCOPE_API_KEY = "sk-ws-H.EEDYEMY.q7Lh.MEYCIQCiuhQZP-WhtdXdsiJiLh0zSBQV8P7gY_mMXh9DE8SQ2AIhAO9BfS9nIkqBdyqXd0xV98xEhvNIo34KfxyjDHJjyYan"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL = "qwen-turbo"
# =================================================

class ToolCall(BaseModel):
    id: str
    function: dict

class LLMResponse(BaseModel):
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]] = None

RETRY_EXCEPTIONS = (TransportError, TimeoutException)

def retry(max_times=2, sleep_sec=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except RETRY_EXCEPTIONS as e:
                    attempt += 1
                    if attempt > max_times:
                        logger.error(f"重试{max_times}次仍然失败: {e}")
                        raise NetworkRequestError(f"请求超时/网络异常")
                    logger.warning(f"网络异常，即将重试第{attempt}次，等待{sleep_sec}s")
                    await asyncio.sleep(sleep_sec)
        return wrapper
    return decorator


@retry(max_times=2)
async def call_llm_with_tool(messages: List[dict], stream: bool = False) -> LLMResponse:
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }

    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_two_numbers",
                "description": "计算两个整数相加",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer"},
                        "b": {"type": "integer"}
                    },
                    "required": ["a", "b"]
                }
            }
        }
    ]

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "tools": tools,
        "stream": stream
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                url=f"{DASHSCOPE_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]
            return LLMResponse(
                content=choice.get("content"),
                tool_calls=choice.get("tool_calls")
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"大模型接口错误：status={e.response.status_code}, text={e.response.text}")
            raise NetworkRequestError(f"接口返回异常：{e.response.status_code}")