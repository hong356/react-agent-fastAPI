import json
from typing import AsyncGenerator
import httpx
from config import DASHSCOPE_API_KEY, MODEL_NAME
from logger import logger

# 内存会话临时存储，测试使用
MEMORY_SESSION = {}

system_prompt = """
你是ReAct智能体，严格遵循思考→行动→观察循环。
可用工具：
get_current_time：获取服务器当前真实时间，返回 YYYY-MM-DD HH:MM:SS。

【强制规则】
1. 你本身不知道当前真实时间，知识库是过时的。
2. 用户问几点、日期、星期，**必须调用 get_current_time，严禁自己编造时间！**
3. 调用工具固定输出格式：
Action: 工具名称
Action Input: 工具参数（无参数就填空字符串）
4. 如果不需要调用工具，直接输出最终回答 Final Answer: xxx
"""

from tools import TOOLS, get_tool_by_name

class Agent:
    def __init__(self, session_id: str):
        self.system_prompt = system_prompt
        self.tools = TOOLS
        self.session_id = session_id

    async def load_history(self):
        """内存读取对话历史"""
        if self.session_id in MEMORY_SESSION:
            history = MEMORY_SESSION[self.session_id]
            logger.info(f"会话 {self.session_id} 加载历史消息，共{len(history)}条")
            return history
        logger.info(f"会话 {self.session_id} 新建会话")
        return []

    async def save_history(self, messages):
        """内存保存对话历史"""
        MEMORY_SESSION[self.session_id] = messages
        logger.info(f"会话 {self.session_id} 消息存入内存")

    async def llm_call(self, messages: list):
        """调用阿里云DashScope"""
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": True
        }
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, headers=headers, json=body) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            obj = json.loads(data)
                            delta = obj["choices"][0]["delta"].get("content", "")
                            yield delta
                        except Exception:
                            continue

    async def run_stream(self, query: str) -> AsyncGenerator[str, None]:
        # 加载历史消息
        history = await self.load_history()
        messages = [{"role": "system", "content": self.system_prompt}] + history
        messages.append({"role": "user", "content": query})

        full_response = ""
        max_loop = 3 # 最多工具调用3轮，防止死循环
        for _ in range(max_loop):
            full_response = ""
            async for chunk in self.llm_call(messages):
                full_response += chunk
                yield chunk
            logger.info(f"模型输出：{full_response}")

            # 判断是否调用工具
            if "Action:" in full_response and "Action Input:" in full_response:
                # 解析工具名称
                lines = full_response.splitlines()
                action_name = ""
                action_input = ""
                for line in lines:
                    if line.startswith("Action:"):
                        action_name = line.replace("Action:", "").strip()
                    if line.startswith("Action Input:"):
                        action_input = line.replace("Action Input:", "").strip()
                logger.info(f"调用工具：{action_name}, 参数：{action_input}")
                # 执行工具
                tool_func = get_tool_by_name(action_name)
                if tool_func is not None:
                    obs = tool_func()
                    logger.info(f"工具返回结果：{obs}")
                    # 追加消息
                    messages.append({"role": "assistant", "content": full_response})
                    messages.append({"role": "user", "content": f"Observation: {obs}"})
                    continue
            else:
                break
        # 保存本次对话
        history.append({"role":"user", "content": query})
        history.append({"role":"assistant", "content": full_response})
        await self.save_history(history)