import asyncio
import threading
import webview
import pyperclip
import sys
from src.utils import resource_path, check_for_updates, __version__ as CURRENT_VERSION
from notifypy import Notify
from .douyin import Douyin
from .bilibili import Bili


thread_lock = threading.Lock()
bili_manager = Bili()
dy_manager = Douyin()


class Api:
    def get_danmu(self):
        """
        Get the list of danmaku from Bilibili.

        Returns:
            list: A list of danmaku from Bilibili.
        """
        with thread_lock:
            return bili_manager.get_list()

    def get_dy_danmu(self):
        """
        Get the list of danmaku from Douyin.

        Returns:
            list: A list of danmaku from Douyin.
        """
        with thread_lock:
            return dy_manager.get_list()

    def minus_window(self):
        """
        Minimize the current window.
        """
        window = webview.active_window()
        if not window:
            return
        window.hide()
        self.send_notification("提示", "主界面已隐藏到托盘图标")

    def check_clipboard(self):
        """
        Check the current clipboard contents.

        Returns:
            str: The current contents of the clipboard.
        """
        return pyperclip.paste()

    def get_bili_ws_status(self):
        """
        Get the status of the Bilibili WebSocket connection.

        Returns:
            int: The status of the Bilibili WebSocket connection. -1 means the connection is not configured, 0 means the connection is not running, and 1 means the connection is running.
        """
        return bili_manager.get_status()

    def get_dy_ws_status(self):
        """
        Get the status of the Douyin WebSocket connection.

        Returns:
            int: The status of the Douyin WebSocket connection. -1 means the connection is not configured, 0 means the connection is not running, and 1 means the connection is running.
        """
        return dy_manager.get_status()

    def reload(self):
        """
        Reload the current page.

        This function will reload the current page by loading the current URL again.

        Returns:
            None
        """
        window = webview.active_window()
        if window:
            window.load_url(window.get_current_url())

    def send_notification(self, title, message):
        notification = Notify()
        notification.application_name = "点歌姬"
        notification.title = title
        notification.message = message
        notification.icon = resource_path("logo.png")
        notification.send(block=False)

    def is_bundle(self):
        is_bundle = getattr(sys, "frozen", False)
        return is_bundle

    def get_version(self):
        """
        Get the current version of the VSingerBoard application.

        Returns:
            str: The current version of the VSingerBoard application.
        """
        return CURRENT_VERSION

    def update_verion(self):
        return check_for_updates()


async def restart_bili():
    bili_manager.stop()
    await asyncio.sleep(1)
    bili_manager.start()


async def restart_dy():
    dy_manager.stop()
    await asyncio.sleep(1)
    dy_manager.start()


def start_bili():
    bili_manager.start()


def start_dy():
    dy_manager.start()


def stop_bili():
    bili_manager.stop()


def stop_dy():
    dy_manager.stop()
