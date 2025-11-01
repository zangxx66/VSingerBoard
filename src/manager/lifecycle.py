import signal
import sys
from .server_manager import stop_all_servers
from . import gui_manager
from src.utils import logger


def signal_handler(sig, frame):
    logger.info(f"Received signal: {sig}. Triggering shutdown.")


def setup_signal_handlers():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGQUIT, signal_handler)


def on_closing():
    if gui_manager.icon:
        gui_manager.icon.stop()
        logger.info("Tray icon stopped.")
        gui_manager.icon = None
    stop_all_servers()
