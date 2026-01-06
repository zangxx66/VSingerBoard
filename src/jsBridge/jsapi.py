import asyncio
import threading
import webview
import pyperclip
from src.utils import async_worker, __version__ as CURRENT_VERSION
from src.live import bili_manager, douyin_manager


thread_lock = threading.Lock()


async def _restart_bili_async():
    await bili_manager.stop()
    await asyncio.sleep(1)
    bili_manager.start()


async def _restart_dy_async():
    await douyin_manager.stop()
    await asyncio.sleep(1)
    douyin_manager.start()


class Api:

    def check_clipboard(self):
        """
        检查当前剪贴板内容。

        Returns:
            str: 剪贴板的当前内容。
        """
        return pyperclip.paste()

    def restart_bilibili_ws(self):
        """
        重新启动Bilibili WebSocket连接。

        此函数将异步重新启动Bilibili WebSocket连接。
        """
        async_worker.submit(_restart_bili_async())

    def restart_douyin_ws(self):
        """
        重新启动抖音WebSocket连接。

        此函数将异步重新启动抖音WebSocket连接。
        """
        async_worker.submit(_restart_dy_async())

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

    def get_version(self):
        """
        获取VSingerBoard应用程序的当前版本。

        Returns:
            str: VSingerBoard应用程序的当前版本。
        """
        return CURRENT_VERSION
