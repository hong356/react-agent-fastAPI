import logging
import sys

# 日志初始化
def setup_logger():
    logger = logging.getLogger("agent")
    logger.setLevel(logging.INFO)

    format_str = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(format_str)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()