import webview
import os
import sys
import time
from webview.window import Window
from PIL import Image
from pystray import Icon, Menu, MenuItem
from src.utils import logger, resource_path, send_notification

icon = None


def on_minimized(window):
    window.hide()
    send_notification("提示", "主界面已隐藏到托盘图标")


def on_start(window: Window):
    logger.info("------window start------")
    webview.logger.debug(f"token:{webview.token}")


def setup_tray(window: Window):
    """
    设置系统托盘图标。

    Args:
        window (Window): 主窗口实例。
    """
    global icon
    if icon:
        return
    logo_dir_path = resource_path("icons")
    logo_path = os.path.join(logo_dir_path, "logo.png")
    image = Image.open(logo_path)

    def show_window(i, item):
        window.show()

    def hide_window(i, item):
        window.hide()

    def quit_app(i, item):
        if window:
            window.destroy()
        icon.stop()

    menu = Menu(
        MenuItem("显示主界面", show_window, default=True),
        MenuItem("隐藏主界面", hide_window),
        Menu.SEPARATOR,
        MenuItem("退出程序", quit_app)
    )

    icon = Icon("VSingerBoard", image, "点歌姬", menu)
    icon.run_detached()


def create_window(DEBUG: bool, api):
    PORT = 5173 if DEBUG else 8000

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
    initWidth = int(screens.width * 0.9)
    initHeight = int(screens.height * 0.9)

    webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    webview.settings['ALLOW_DOWNLOADS'] = True
    webview.settings["SHOW_DEFAULT_MENUS"] = False
    os.environ["PYWEBVIE_WLOG"] = "debug"

    window = webview.create_window("点歌姬",
                                   url=f"http://127.0.0.1:{PORT}/",
                                   js_api=api,
                                   localization=localization,
                                   width=initWidth,
                                   height=initHeight,
                                   resizable=False,
                                   easy_drag=False,)
    window.events.minimized += on_minimized
    return window


def terminal_progress(total_iterations, bar_length=40):
    for i in range(total_iterations + 1):
        filled_length = int(bar_length * i // total_iterations)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r{bar}")
        sys.stdout.flush()
        time.sleep(0.05)
