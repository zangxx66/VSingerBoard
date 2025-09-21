import asyncio
import threading
import webview
import pyperclip
import time
import requests
from src.bili import MyLive
from src.database import Db
from src.douyin import DouyinLiveWebFetcher
from bilibili_api import Credential
from src.utils import logger
from src.utils import __version__ as CURRENT_VERSION


BdanmuList: list = []
DdanmuList: list = []
bili_thread: threading.Thread = None
dy_thread: threading.Thread = None


class Api:
    def __init__(self):
        self.window = None

    def get_danmu(self):
        """
        Get the list of danmu messages received from Bili.

        The list will be cleared after calling this method.

        Returns:
            list: A copy of the list of danmu messages
        """
        if len(BdanmuList) > 0:
            result = BdanmuList.copy()
            BdanmuList.clear()
            return result

    def get_dy_danmu(self):
        """
        Get the list of danmu messages received from Douyin.

        The list will be cleared after calling this method.

        Returns:
            list: A copy of the list of danmu messages
        """
        if len(DdanmuList) > 0:
            result = DdanmuList.copy()
            DdanmuList.clear()
            return result

    def minus_window(self):
        """
        Minimize the current window.

        If there is no active window, this method does nothing.
        """
        window = webview.active_window()
        if not window:
            return
        window.minimize()

    def copy_to_clipboard(self, text):
        """
        Copy the given text to the clipboard.

        Args:
            text (str): The text to copy to the clipboard
        """
        pyperclip.copy(text)

    def check_clipboard(self):
        """
        Get the content of the clipboard.

        Returns:
            str: The content of the clipboard
        """
        clipboard_content = pyperclip.paste()
        return clipboard_content

    def get_version(self):
        """
        Get the current version of the project.

        Returns:
            str: The current version of the project
        """
        return CURRENT_VERSION

    def check_for_updates(self):
        """
        Check for updates of VSingerBoard.

        This method sends a GET request to the GitHub API to fetch the latest release information.

        If the latest version is newer than the current version, it returns a dictionary containing the version number, URL to the latest release, and a message indicating the update.

        If the latest version is the same as the current version, it returns a dictionary containing the current version number, an empty URL, and a message indicating that the current version is the latest.

        If the request fails, it returns a dictionary containing the current version number, an empty URL, and a message indicating the failure.

        If an unexpected error occurs, it returns a dictionary containing the current version number, an empty URL, and a message indicating the error.

        Returns:
            dict: A dictionary containing information about the update
        """
        REPO_URL = "https://api.github.com/repos/zangxx66/VSingerBoard/releases/latest"

        def compare_versions(v1, v2):
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]

            # 填充较短的版本号以进行比较
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            if v1_parts > v2_parts:
                return 1
            elif v1_parts < v2_parts:
                return -1
            else:
                return 0

        try:
            response = requests.get(REPO_URL)
            response.raise_for_status()  # 如果请求失败，则引发 HTTPError

            latest_release = response.json()
            latest_version = latest_release["tag_name"]

            # 比较版本号
            if compare_versions(latest_version, CURRENT_VERSION) > 0:
                return {
                    "code": 0,
                    "version": latest_version,
                    "url": latest_release["html_url"],
                    "msg": f"发现新版本: {latest_version} (当前版本: {CURRENT_VERSION})"
                }
            else:
                return {
                    "code": 0,
                    "version": CURRENT_VERSION,
                    "url": "",
                    "msg": "当前已是最新版本。"
                }
        except requests.exceptions.RequestException as e:
            logger.exception(f"检查更新失败: {e}")
            return {
                "code": -1,
                "version": CURRENT_VERSION,
                "url": "",
                "msg": "检查更新失败"
            }
        except Exception as e:
            logger.exception(f"检查更新发生未知错误: {e}")
            return {
                "code": -1,
                "version": CURRENT_VERSION,
                "url": "",
                "msg": "发生未知错误"
            }


class Bili:
    conn: Db

    def __init__(self):
        self.conn = Db()

    def start(self):
        """
        Wrapper to run the async start method in a new event loop.
        This method is the target for the background thread.
        """
        try:
            asyncio.run(self._start_async())
        except Exception as e:
            webview.logger.error(f"Bilibili thread failed: {e}")

    async def _start_async(self):
        """
        Asynchronously fetches configuration and starts the Bilibili live client.
        """
        config = await self.conn.get_bconfig()
        if not config or config.room_id == 0:
            webview.logger.info("Bilibili room_id not configured, skipping.")
            return

        bili_credential = await self.conn.get_bcredential(enable=True)
        credential: Credential = None
        if bili_credential:
            credential = Credential(
                sessdata=bili_credential.sessdata,
                jct=bili_credential.bili_jct,
                buvid3=bili_credential.buvid3,
                buvid4=bili_credential.buvid4,
                dedeuserid=bili_credential.dedeuserid,
                ac_time_value=bili_credential.ac_time_value
            )

        live = MyLive(room_id=config.room_id, credentials=credential, song_prefix=config.sing_prefix)
        live.on("danmu")(self.add_bdanmu)
        live.on("sc")(self.add_bdanmu)

        if hasattr(live, "connect") and asyncio.iscoroutinefunction(live.connect):
            await live.connect()
        else:
            webview.logger.error("MyLive object does not have a suitable async 'connect' method.")

    def add_bdanmu(self, danmu):
        global BdanmuList
        result = {
            "uid": danmu["uid"],
            "uname": danmu["uname"],
            "msg": danmu["msg"],
            "send_time": danmu["send_time"],
            "source": "bilibili"
        }
        BdanmuList.append(result)


class Douyin:
    conn: Db

    def __init__(self):
        self.conn = Db()
        self.sing_prefix = ""

    def start(self):
        """
        Wrapper to run the async start method in a new event loop.
        This method is the target for the background thread.
        """
        try:
            asyncio.run(self._start_async())
        except Exception as e:
            webview.logger.error(f"Douyin thread failed: {e}")

    async def _start_async(self):
        """
        Asynchronously fetches configuration and starts the Douyin live client.
        """
        config = await self.conn.get_dy_config()
        if not config or not config.room_id:
            webview.logger.info("Douyin room_id not configured, skipping.")
            return

        self.sing_prefix = config.sing_prefix

        # Assuming DouyinLiveWebFetcher follows a similar pattern with an async start/connect
        Dlive = DouyinLiveWebFetcher(live_id=config.room_id)
        Dlive.on("danmu")(self.add_dydanmu)

        # Similar to Bili, we need to call an async method to start the client
        if hasattr(Dlive, "connect") and asyncio.iscoroutinefunction(Dlive.connect):
            await Dlive.connect()
        elif hasattr(Dlive, "start") and asyncio.iscoroutinefunction(Dlive.start):
            await Dlive.start()
        else:
            # If the start method is synchronous and blocking, it must be called directly.
            # This assumes it manages its own loop correctly without conflicting.
            Dlive.start()

    def add_dydanmu(self, danmu):
        global DdanmuList
        if danmu.content.startswith(self.sing_prefix):
            song_name = danmu.content.replace(self.sing_prefix, "").strip()
            result = {
                "uid": danmu.user_id,
                "uname": danmu.user_name,
                "msg": song_name,
                "send_time": int(time.time()),
                "source": "douyin"
            }
            DdanmuList.append(result)


async def restart_bili():
    stop_bili()
    start_bili()


async def restart_dy():
    stop_dy()
    start_dy()


def start_bili():
    global bili_thread
    bili = Bili()
    bili_thread = threading.Thread(target=bili.start, daemon=True, name="bili_thread")
    bili_thread.start()


def start_dy():
    global dy_thread
    dy = Douyin()
    dy_thread = threading.Thread(target=dy.start, daemon=True, name="dy_thread")
    dy_thread.start()


def stop_bili():
    global bili_thread
    if bili_thread is not None and bili_thread.is_alive():
        bili_thread.join(5)
        webview.logger.info("Waiting for bili thread to finish...")


def stop_dy():
    global dy_thread
    if dy_thread is not None and dy_thread.is_alive():
        dy_thread.join(5)
        webview.logger.info("Waiting for dy thread to finish...")
