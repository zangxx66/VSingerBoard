import asyncio
import threading
import webview
import pyperclip
import time
from src.bili import MyLive
from src.database import Db
from src.douyin import DouyinLiveWebFetcher
from bilibili_api import Credential


BdanmuList: list = []
DdanmuList: list = []
bili_thread: threading.Thread = None
dy_thread: threading.Thread = None


class Api:
    def get_danmu(self):
        if len(BdanmuList) > 0:
            result = BdanmuList.copy()
            BdanmuList.clear()
            return result

    def get_dy_danmu(self):
        if len(DdanmuList) > 0:
            result = DdanmuList.copy()
            DdanmuList.clear()
            return result

    def minus_window(self):
        window = webview.active_window()
        if not window:
            return
        window.minimize()

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)

    def check_clipboard(self):
        clipboard_content = pyperclip.paste()
        return clipboard_content


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
