import logging
import sys

class ColorFormatter(logging.Formatter):
    # 定义不同级别日志的颜色
    COLOR_MAP = {
        logging.DEBUG: '\033[1;32m', # 绿色
        logging.INFO: '\033[1;34m', # 蓝色
        logging.WARNING: '\033[1;33m', # 黄色
        logging.ERROR: '\033[1;31m', # 红色
        logging.CRITICAL: '\033[1;41m', # 红底白字
    }

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)

    def format(self, record):
        # 根据日志级别添加颜色
        record.color = self.COLOR_MAP.get(record.levelno, '')
        record.reset_color = '\033[0m'
        return super().format(record)

# 创建logger对象
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建控制台handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# 设置handler的Formatter为自定义的ColorFormatter
formatter = ColorFormatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)

# 将handler添加到logger
logger.addHandler(console_handler)

# 输出日志
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')