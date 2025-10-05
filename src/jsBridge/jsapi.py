import asyncio
import threading
import webview
import pyperclip
import sys
from src.utils import check_for_updates, async_worker, __version__ as CURRENT_VERSION
from src.notifypy import Notify
from .douyin import Douyin
from .bilibili import Bili


thread_lock = threading.Lock()
bili_manager = Bili()
dy_manager = Douyin()


class Api:
    def get_danmu(self):
        """
        获取Bilibili的弹幕列表。

        Returns:
            list: Bilibili的弹幕列表。
        """
        with thread_lock:
            return bili_manager.get_list()

    def get_dy_danmu(self):
        """
        获取抖音的弹幕列表。

        Returns:
            list: 抖音的弹幕列表。
        """
        with thread_lock:
            return dy_manager.get_list()

    def minus_window(self):
        """
        最小化当前窗口。
        """
        window = webview.active_window()
        if not window:
            return
        window.hide()
        self.send_notification("提示", "主界面已隐藏到托盘图标")

    def check_clipboard(self):
        """
        检查当前剪贴板内容。

        Returns:
            str: 剪贴板的当前内容。
        """
        return pyperclip.paste()

    def get_bili_ws_status(self):
        """
        获取Bilibili WebSocket连接的状态。

        Returns:
            int: Bilibili WebSocket连接的状态。-1表示连接未配置，0表示连接未运行，1表示连接正在运行。
        """
        return bili_manager.get_status()

    def get_dy_ws_status(self):
        """
        获取抖音WebSocket连接的状态。

        Returns:
            int: 抖音WebSocket连接的状态。-1表示连接未配置，0表示连接未运行，1表示连接正在运行。
        """
        return dy_manager.get_status()

    def reload(self):
        """
        重新加载当前页面。

        此函数将通过再次加载当前URL来重新加载当前页面。

        Returns:
            None
        """
        window = webview.active_window()
        if window:
            window.load_url(window.get_current_url())

    def send_notification(self, title, message):
        """
        发送桌面通知。

        Args:
            title (str): 通知标题。
            message (str): 通知内容。

        Returns:
            None
        """
        notification = Notify(enable_logging=True)
        notification.application_name = "点歌姬"
        notification.title = title
        notification.message = message
        notification.send(block=False)

    def is_bundle(self):
        """
        检查当前Python环境是否是bundle环境。

        在bundle环境中，sys.frozen将被设置为True。

        Returns:
            bool: 当前Python环境是否是bundle环境。
        """
        is_bundle = getattr(sys, "frozen", False)
        return is_bundle

    def get_version(self):
        """
        获取VSingerBoard应用程序的当前版本。

        Returns:
            str: VSingerBoard应用程序的当前版本。
        """
        return CURRENT_VERSION

    def update_verion(self):
        """
        检查VSingerBoard应用程序的最新版本信息。

        Returns:
            dict: VSingerBoard应用程序的最新版本信息。
        """
        return check_for_updates()


async def _restart_bili_async():
    bili_manager.stop()
    await asyncio.sleep(1)
    bili_manager.start()


async def _restart_dy_async():
    await dy_manager.stop()
    await asyncio.sleep(1)
    dy_manager.start()


def restart_bili():
    async_worker.submit(_restart_bili_async())


def restart_dy():
    async_worker.submit(_restart_dy_async())


def start_bili():
    bili_manager.start()


def start_dy():
    dy_manager.start()


def stop_bili():
    async_worker.submit(bili_manager.stop())


def stop_dy():
    async_worker.submit(dy_manager.stop())
