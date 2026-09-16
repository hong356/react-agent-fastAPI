import logging
from config import LOG_LEVEL, LOG_FILE

def setup_logger():
    logger = logging.getLogger("ReActAgent")
    logger.setLevel(LOG_LEVEL)
    # 防止重复添加handler
    if logger.handlers:
        return logger

    # 输出到文件
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 输出到控制台
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()