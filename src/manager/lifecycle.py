import signal
import sys
from .server_manager import stop_all_servers
from .ipc_handler import stop_ipc_task
from src.utils import logger


def signal_handler(sig, frame):
    logger.info(f"Received signal: {sig}. Triggering shutdown.")
    on_closing()


def setup_signal_handlers():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGQUIT, signal_handler)


def on_closing():
    stop_all_servers()
    stop_ipc_task()
