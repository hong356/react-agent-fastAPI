import asyncio
import logging
from functools import wraps
from httpx import TransportError, TimeoutException

logger = logging.getLogger("agent")
# 仅这些临时异常允许重试
RETRY_EXC = (TransportError, TimeoutException)


def async_retry(max_times=2, sleep_sec=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except RETRY_EXC as e:
                    attempt += 1
                    if attempt > max_times:
                        logger.error(f"重试{max_times}次仍然失败 | 异常:{e}")
                        raise
                    logger.warning(f"网络临时异常，等待{sleep_sec}s，第{attempt}次重试")
                    await asyncio.sleep(sleep_sec)
        return wrapper
    return decorator