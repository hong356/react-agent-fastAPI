# 自定义异常
class NetworkRequestError(Exception):
    """网络请求异常"""
    pass

class ParamsInvalidError(Exception):
    """参数错误"""
    pass

class ToolExecuteError(Exception):
    """工具执行异常"""
    pass