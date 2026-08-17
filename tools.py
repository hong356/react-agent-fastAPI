from typing import Dict
from exceptions import ToolExecuteError
from logger_setup import logger

# 工具函数定义
def add_two_numbers(a: int, b: int) -> int:
    """两个数字相加"""
    return a + b

# 工具注册表
TOOL_REGISTRY = {
    "add_two_numbers": add_two_numbers
}

def run_tool(tool_call) -> str:
    """执行工具调用"""
    try:
        import json
        func_name = tool_call.function["name"]
        arguments = json.loads(tool_call.function["arguments"])

        if func_name not in TOOL_REGISTRY:
            return f"工具不存在：{func_name}"

        func = TOOL_REGISTRY[func_name]
        result = func(**arguments)
        return str(result)
    except Exception as e:
        logger.error(f"工具执行失败: {e}")
        raise ToolExecuteError(f"工具运行异常:{e}")