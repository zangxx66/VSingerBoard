import logging
import datetime
import sys
from .tool import get_path

file_name = f"{datetime.datetime.today().strftime('%Y-%m-%d')}.log"
dir_path = get_path(file_name, dir_name="logs")

logger = logging.getLogger("danmaku")
file_handle = logging.FileHandler(filename=dir_path, mode="a", encoding="utf8")
file_formatter = logging.Formatter(fmt="[%(asctime)s][%(levelname)s][%(module)s][%(funcName)s][%(lineno)d] - %(message)s", datefmt="%Y-%m-%d  %H:%M:%S")
file_handle.setFormatter(file_formatter)
logger.addHandler(file_handle)

# 根据环境设置日志级别
if 'pydevd' in sys.modules or 'debugpy' in sys.modules:
    # 开发环境
    console_handle = logging.StreamHandler()
    console_handle.setFormatter(file_formatter)
    logger.addHandler(console_handle)
    logger.setLevel(logging.DEBUG)
    console_handle.setLevel(logging.DEBUG)
else:
    # 打包环境
    logger.setLevel(logging.INFO)
    file_handle.setLevel(logging.WARNING)


def exception_handle(exc_type, exc_obj, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_obj, exc_traceback)
        return
    logger.critical("Unhandled Exception", exc_info=(exc_type, exc_obj, exc_traceback))


sys.excepthook = exception_handle
