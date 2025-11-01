import sys
import os
import time
import webview
from src.utils import logger, async_worker
from src.manager import gui_manager, lifecycle, server_manager, version_manager
from src.jsBridge import Api


def main():
    logger.info("------ Application Startup ------")

    # 注册信号处理
    lifecycle.setup_signal_handlers()

    # 启动异步任务
    async_worker.start()

    # 启动FastApi
    server_manager.start_http_server()

    DEBUG = not getattr(sys, "frozen", False)
    if DEBUG:
        version_manager.update_build()
        # 启动Vite
        server_manager.start_vite_server()
        time.sleep(3)

    # 启动websocket
    server_manager.start_websocket_server()

    api = Api()
    window = gui_manager.create_window(DEBUG, api)
    window.events.closing += lifecycle.on_closing
    gui_manager.setup_tray(window)
    webview.start(gui_manager.on_start, window, debug=DEBUG)


def run_app():
    try:
        main()
    except Exception as ex:
        logger.exception(ex)
    finally:
        lifecycle.on_closing()
        async_worker.stop()
        os._exit(0)


if __name__ == "__main__":
    run_app()
