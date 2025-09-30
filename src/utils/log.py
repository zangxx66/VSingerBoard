import logging
import datetime
import sys
from .tool import get_path

file_name = f"{datetime.datetime.today().strftime('%Y-%m-%d')}.log"
dir_path = get_path(file_name, dir_name="logs")

logger = logging.getLogger("danmaku")
file_handle = logging.FileHandler(filename=dir_path, mode="a", encoding="utf8")
console_handle = logging.StreamHandler()

file_formatter = logging.Formatter(fmt="[%(asctime)s][%(levelname)s][%(module)s][%(funcName)s][%(lineno)d] - %(message)s", datefmt="%Y-%m-%d  %H:%M:%S")

logger.setLevel(logging.DEBUG)
# 是否正在以调试模式运行
if 'pydevd' in sys.modules or 'debugpy' in sys.modules:
    print("【调试模式】")
    console_handle.setLevel(logging.DEBUG)
else:
    print("【正式模式】")
    console_handle.setLevel(logging.INFO)
file_handle.setLevel(logging.WARNING)

file_handle.setFormatter(file_formatter)
console_handle.setFormatter(file_formatter)


def exception_handle(exc_type, exc_obj, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_obj, exc_traceback)
        return
    logger.exception("Unhandled Exception", exc_info=(exc_type, exc_obj, exc_traceback))


sys.excepthook = exception_handle

if not logger.hasHandlers():
    logger.addHandler(file_handle)
    logger.addHandler(console_handle)
