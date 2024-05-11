from logtail import LogtailHandler
import logging
from ..config.globals import settings


def setup_logger(logger_name, log_file=None):
    # 创建日志记录器
    level = logging.INFO

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 创建logtail处理器
    logtail_handler = LogtailHandler(source_token=settings.LOG_SERVICE_TOKEN)
    logtail_handler.setLevel(level)
    logtail_handler.setFormatter(formatter)
    logger.addHandler(logtail_handler)

    # 如果指定了日志文件，则创建文件处理器并将其添加到日志记录器
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
