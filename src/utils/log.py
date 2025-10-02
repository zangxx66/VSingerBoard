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

# Set log levels based on environment
if getattr(sys, 'frozen', False):
    # Packaged app
    logger.setLevel(logging.INFO)
    file_handle.setLevel(logging.WARNING)
else:
    # Development environment
    console_handle = logging.StreamHandler()
    console_handle.setFormatter(file_formatter)
    logger.addHandler(console_handle)
    logger.setLevel(logging.DEBUG)
    console_handle.setLevel(logging.DEBUG)


def exception_handle(exc_type, exc_obj, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_obj, exc_traceback)
        return
    logger.critical("Unhandled Exception", exc_info=(exc_type, exc_obj, exc_traceback))


sys.excepthook = exception_handle
