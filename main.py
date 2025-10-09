import sys
import os
import webview
import threading
import time
from src.utils import async_worker, logger
from src.manager import gui_manager, ipc_handler, lifecycle, server_manager, version_manager


def main():
    logger.info("------ Application Startup ------")

    lifecycle.setup_signal_handlers()

    async_worker.start()

    server_manager.start_http_server(webview.token, ipc_handler.ipc_manager)

    DEBUG = not getattr(sys, "frozen", False)
    if DEBUG:
        version_manager.update_build()
        dev_thread = threading.Thread(target=server_manager.start_vite_server, daemon=True, name="ViteServer")
        dev_thread.start()
        time.sleep(3)

    server_manager.start_websocket_server()
    ipc_handler.start_ipc_task()

    window = gui_manager.create_window(DEBUG)
    window.events.closing += lifecycle.on_closing
    gui_manager.setup_tray(window)
    webview.start(gui_manager.on_start, window, debug=DEBUG, gui="gtk")


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        logger.exception(ex)
    finally:
        # lifecycle.on_closing()
        async_worker.stop()
        os._exit(0)
