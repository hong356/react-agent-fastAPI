import datetime

def get_current_time() -> str:
    """获取服务器当前真实时间
    用户询问几点、日期、星期时调用
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# 工具列表：字典结构，只把名称、描述传给大模型，函数本体留在代码内部
TOOLS = [
    {
        "name": "get_current_time",
        "description": "获取服务器当前真实时间，返回格式 YYYY-MM-DD HH:MM:SS",
        "func": get_current_time
    }
]

# 根据工具名找到对应的函数
def get_tool_by_name(tool_name: str):
    for tool in TOOLS:
        if tool["name"] == tool_name:
            return tool["func"]
    return None