import re
import os
import sys
import threading
import time
import signal
import subprocess
import webview
from PIL import Image
from pystray import Icon, Menu, MenuItem
from src.utils import logger, resource_path
from src.server import startup
from src.jsBridge import Api, start_bili, start_dy, stop_bili, stop_dy
from webview.window import Window


server_thread: threading.Thread = None
dev_thread: threading.Thread = None
dev_process = None
icon = None


def signal_handler(sig, frame):
    logger.info(f"Received signal: {sig}. Triggering shutdown.")
    on_closing()


def pro_server():
    logger.info("------start HTTP server------")
    startup()


def ws_server():
    logger.info("------start websocket------")
    start_dy()
    start_bili()


def dev_server():
    global dev_process
    dev_process = subprocess.Popen("npm run -C frontend/ dev", shell=True)
    dev_process.communicate()
    logger.info("------startup Vite server------")


def on_start(window: Window):
    webview.logger.info("------window start------")
    webview.logger.debug(f"token:{webview.token}")


def on_closing():
    webview.logger.info("Window closing event triggered.")
    stop_bili()
    stop_dy()

    if dev_process is not None:
        dev_process.terminate()
    if icon is not None:
        icon.stop()

    logger.info("Cleanup complete. Forcing exit.")
    os._exit(0)


def setup_tray(window: Window):
    global icon
    logo_dir_path = resource_path("icons")
    logo_path = os.path.join(logo_dir_path, "logo.png")
    image = Image.open(logo_path)

    def show_window(i, item):
        window.show()

    def hide_window(i, item):
        window.hide()

    def quit_app(i, item):
        window.destroy()
        i.stop()

    menu = Menu(
        MenuItem("显示主界面", show_window, default=True),
        MenuItem("隐藏主界面", hide_window),
        Menu.SEPARATOR,
        MenuItem("退出程序", quit_app)
    )

    icon = Icon("VSingerBoard", image, "点歌姬", menu)
    icon.run_detached()


def main():
    global server_thread, dev_thread
    logger.info("------startup------")

    # Setup signal handlers to gracefully shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGQUIT, signal_handler)

    # 是否在PyInstaller环境
    DEBUG = not getattr(sys, "frozen", False)
    PORT = 5173 if DEBUG else 8000

    if DEBUG:
        try:
            version_path = 'version.txt'
            if os.path.exists(version_path):
                with open(version_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 使用正则找到Build
                match = re.search(r"stringStruct\(u'Build',\s*u'(\d+)'\)", content)
                if match:
                    current_build_number = int(match.group(1))
                    new_build_number = current_build_number + 1
                    # 使用新的Build替换
                    new_content = re.sub(
                        r"(stringStruct\(u'Build',\s*u')(\d+)(')",
                        r"\g<1>" + str(new_build_number) + r"\g<3>",
                        content
                    )
                    with open(version_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    logger.info(f"Updated build number in version.txt from {current_build_number} to {new_build_number}")
                else:
                    logger.warning("Could not find 'Build' number in version.txt")
        except Exception as e:
            logger.error(f"Failed to update build number: {e}")

    try:
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
        screens = webview.screens[0]
        # 程序窗口大小
        initWidth = int(screens.width / 1.2)
        initHeight = int(screens.height / 1.2)

        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
        webview.settings['ALLOW_DOWNLOADS'] = True
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

        window.expose(on_closing)

        if DEBUG:
            dev_thread = threading.Thread(target=dev_server, daemon=True, name="devServer")
            dev_thread.start()
            # Vite服务器启动较慢，手动给个时间等待
            time.sleep(3)

        server_thread = threading.Thread(target=pro_server, daemon=True, name="proServer")
        server_thread.start()

        ws_server()

        setup_tray(window)

        webview.start(on_start, window, debug=DEBUG, gui="gtk")

    except Exception as ex:
        logger.exception(ex)
    finally:
        # This block will likely not be reached because shutdown() calls os._exit()
        logger.info("Main function finally block reached.")
        on_closing()


if __name__ == "__main__":
    main()
