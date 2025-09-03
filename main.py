import webview
import os
from src.server import app

DEBUG = True
PORT = 8000


def on_server(window):
    if DEBUG:
        os.system("npm run -C frontend/ dev")
    else:
        app.startup()


def main():
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

    PORT = 5173 if DEBUG else 8000
    window = webview.create_window("点歌板", server=app, url=f"http://127.0.0.1:{PORT}/", localization=localization, confirm_close=True, width=1024, height=768)
    webview.start(on_server, window, debug=DEBUG)


if __name__ == "__main__":
    main()
