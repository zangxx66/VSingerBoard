import webview
import os
import asyncio
import threading
import time
from src.server import app
from src.database import Db as conn
from src.utils import logger
from webview.window import Window

DEBUG = True
PORT = 5173 if DEBUG else 8000
window: Window = None


class JsAPI:
    def getWindowHeight(self):
        screens = webview.screens
        screens = screens[0]
        height = screens.height
        initHeight = int(height * 4 / 5)
        return initHeight


def pro_server():
    app.startup()


def dev_server():
    os.system("npm run -C frontend/ dev")
    logger.info("startup dev server")


def on_start(window: Window):
    # window.load_url(f"http://127.0.0.1:{PORT}/")
    window.evaluate_js("alert('启动成功...正在加载')")
    logger.info("window start")
    time.sleep(5)
    window.load_url(f"http://127.0.0.1:{PORT}/")


def main():
    global window
    logger.info("------startup------")

    server_thread: threading.Thread = None
    dev_thread: threading.Thread = None

    try:
        # Initialize services
        asyncio.run(conn.init())

        localization = {
            'global.quitConfirmation': u'你想退出吗？',
            'global.ok': u'确定',
            'global.quit': u'退出',
            'global.cancel': u'取消',
            'global.saveFile': u'保存文件',
            'cocoa.menu.about': u'关于',
            'cocoa.menu.services': u'服务',
            'cocoa.menu.view': u'显示',
            'cocoa.menu.hide': u'隐藏',
            'cocoa.menu.hideOthers': u'隐藏其他',
            'cocoa.menu.showAll': u'显示所有',
            'cocoa.menu.quit': u'退出',
            'cocoa.menu.fullscreen': u'进入全屏',
            'windows.fileFilter.allFiles': u'所有文件',
            'windows.fileFilter.otherFiles': u'其他文件类型',
            'linux.openFile': u'打开文件',
            'linux.openFiles': u'打开多个文件',
            'linux.openFolder': u'打开文件夹',
        }

        if DEBUG:
            dev_thread = threading.Thread(target=dev_server, daemon=True, name="devServer")
            dev_thread.start()
        server_thread = threading.Thread(target=pro_server, daemon=True, name="proServer")
        server_thread.start()

        # 系统分辨率
        screens = webview.screens
        screens = screens[0]
        width = screens.width
        height = screens.height
        # 程序窗口大小
        initWidth = int(width * 2 / 2)
        initHeight = int(height * 4 / 4)

        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
        os.environ["PYWEBVIE_WLOG"] = "debug"

        window = webview.create_window("点歌板", html="<html></html>", js_api=JsAPI(), localization=localization, width=initWidth, height=initHeight, resizable=False)
        webview.start(on_start, window, debug=DEBUG, gui="gtk", icon="wwwroot/assets/images/logo.png")

        # webview.start(on_server, window, debug=DEBUG)
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

        logger.info("Shutdown complete.")  # Wait


if __name__ == "__main__":
    main()
