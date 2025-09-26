import webview
import os
import threading
import time
import signal
import sys
from src.server import startup
from src.utils import logger
from src.jsBridge import Api, start_bili, start_dy, stop_bili, stop_dy
from webview.window import Window

server_thread: threading.Thread = None
dev_thread: threading.Thread = None
stop_event = threading.Event()


def signal_handler(sig, frame):
    logger.info("Received signal:", sig)
    stop_event.set()


def pro_server():
    startup()


def ws_server():
    logger.info("------start websocket------")
    start_dy()
    start_bili()


def dev_server():
    os.system("npm run -C frontend/ dev")
    logger.info("startup dev server")


def on_start(window: Window):
    webview.logger.info("window start")
    webview.logger.debug(f"token:{webview.token}")


def on_closing():
    global stop_event, server_thread, dev_thread
    webview.logger.info("click close")

    stop_event.set()
    if server_thread is not None and server_thread.is_alive:
        webview.logger.info("Waiting for server thread to finish...")
        server_thread.join(5)
    if dev_thread is not None and dev_thread.is_alive:
        webview.logger.info("Waiting for dev thread to finish...")
        dev_thread.join(5)
    stop_bili()
    stop_dy()
    # asyncio.run(conn.disconnect())

    os._exit(0)


def main():
    global stop_event, server_thread, dev_thread
    logger.info("------startup------")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    # 是否在PyInstaller环境
    DEBUG = not getattr(sys, "frozen", False)

    PORT = 5173 if DEBUG else 8000

    try:
        # Initialize services
        # asyncio.run(conn.init())

        localization = {
            'global.quitConfirmation': u'是否退出？',
            'global.ok': u'确定',
            'global.quit': u'退出',
            'global.cancel': u'取消',
            'global.saveFile': u'保存文件',
            'cocoa.menu.about': u'关于',
            'cocoa.menu.services': u'服务',
            'cocoa.menu.view': u'视图',
            'cocoa.menu.edit': u'编辑',
            'cocoa.menu.hide': u'隐藏',
            'cocoa.menu.hideOthers': u'隐藏其他',
            'cocoa.menu.showAll': u'全部显示',
            'cocoa.menu.quit': u'退出',
            'cocoa.menu.fullscreen': u'进入全屏',
            'cocoa.menu.cut': u'剪切',
            'cocoa.menu.copy': u'拷贝',
            'cocoa.menu.paste': u'粘贴',
            'cocoa.menu.selectAll': u'全部选择',
            'windows.fileFilter.allFiles': u'所有文件',
            'windows.fileFilter.otherFiles': u'其他文件类型',
            'linux.openFile': u'打开文件',
            'linux.openFiles': u'打开多个文件',
            'linux.openFolder': u'打开文件夹',
        }

        # 系统分辨率
        screens = webview.screens
        screens = screens[0]
        width = screens.width
        height = screens.height
        # 程序窗口大小
        initWidth = int(width / 1.2)
        initHeight = int(height / 1.2)

        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
        os.environ["PYWEBVIE_WLOG"] = "debug"

        api = Api()
        window = webview.create_window("点歌姬",
                                       url=f"http://127.0.0.1:{PORT}/",
                                       js_api=api,
                                       localization=localization,
                                       width=initWidth,
                                       height=initHeight,
                                       resizable=False,
                                       frameless=True,
                                       easy_drag=True,)

        if DEBUG:
            dev_thread = threading.Thread(target=dev_server, daemon=True, name="devServer")
            dev_thread.start()
            # Vite服务器启动较慢，手动给个时间等待
            time.sleep(3)
        server_thread = threading.Thread(target=pro_server, daemon=True, name="proServer")
        server_thread.start()

        ws_server()
        # window.events.closing += on_closing
        window.expose(on_closing)
        webview.start(on_start, window, debug=DEBUG, gui="gtk", icon="logo.icns")

        stop_event.wait()
    except Exception as ex:
        logger.exception(ex)
    finally:
        logger.info("Shutting down services...")

        if server_thread is not None and server_thread.is_alive:
            logger.info("Waiting for server thread to finish...")
            server_thread.join(5)
        if dev_thread is not None and dev_thread.is_alive:
            logger.info("Waiting for dev thread to finish...")
            dev_thread.join(5)
        stop_bili()
        stop_dy()

        logger.info("Shutdown complete.")  # Wait
        os._exit(0)


if __name__ == "__main__":
    main()
