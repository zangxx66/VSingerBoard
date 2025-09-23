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
from src.utils import logger, __version__ as CURRENT_VERSION


BdanmuList: list = []
DdanmuList: list = []


class Api:
    def __init__(self):
        self.window = None

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
        return pyperclip.paste()

    def get_version(self):
        return CURRENT_VERSION

    def check_for_updates(self):
        REPO_URL = "https://api.github.com/repos/zangxx66/VSingerBoard/releases/latest"

        def compare_versions(v1, v2):
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            if v1_parts > v2_parts: return 1
            if v1_parts < v2_parts: return -1
            return 0

        try:
            response = requests.get(REPO_URL)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            if compare_versions(latest_version, CURRENT_VERSION) > 0:
                return {"code": 0, "version": latest_version, "url": latest_release["html_url"], "body": latest_release["body"], "published_at": latest_release["published_at"], "msg": f"发现新版本: {latest_version} (当前版本: {CURRENT_VERSION})"}
            else:
                return {"code": 0, "version": CURRENT_VERSION, "url": "", "body": latest_release["body"], "published_at": latest_release["published_at"], "msg": "当前已是最新版本。"}
        except Exception as e:
            logger.exception(f"检查更新失败: {e}")
            return {"code": -1, "version": CURRENT_VERSION, "url": "", "body": "", "published_at": "", "msg": "检查更新失败"}


class AsyncWorker:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="async_worker")
        self._db_init_task = None
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def run_blocking(self, func, *args):
        return self._loop.run_in_executor(None, func, *args)

    async def init_db(self):
        if self._db_init_task and not self._db_init_task.done():
            await self._db_init_task
            return
        if Db._initialized:
            return

        self._db_init_task = self._loop.create_task(Db.init())
        await self._db_init_task

    async def disconnect_db(self):
        await Db.disconnect()


async_worker = AsyncWorker()


class Bili:
    def __init__(self):
        self.live = None
        self._run_future = None

    def start(self):
        if self._run_future and not self._run_future.done():
            return
        self._run_future = async_worker.submit(self._start_and_run_client())

    async def _start_and_run_client(self):
        try:
            await async_worker.init_db()
            config = await Db.get_bconfig()
            if not config or config.room_id == 0:
                webview.logger.info("Bilibili room_id not configured, skipping.")
                return

            bili_credential = await Db.get_bcredential(enable=True)
            credential = Credential(**bili_credential.__dict__) if bili_credential else None

            self.live = MyLive(room_id=config.room_id, credentials=credential, song_prefix=config.sing_prefix)
            self.live.on("danmu")(self.add_bdanmu)
            self.live.on("sc")(self.add_bdanmu)

            webview.logger.info("Bilibili live client starting.")
            await async_worker.run_blocking(self.live.start)
        except Exception as e:
            webview.logger.error(f"Bilibili task failed: {e}")
        finally:
            webview.logger.info("Bilibili live client stopped.")

    def stop(self):
        if self.live:
            threading.Thread(target=self.live.stop).start()
        if self._run_future:
            self._run_future.cancel()

    def add_bdanmu(self, danmu):
        BdanmuList.append({"uid": danmu["uid"], "uname": danmu["uname"], "msg": danmu["msg"], "send_time": danmu["send_time"], "source": "bilibili"})


class Douyin:
    def __init__(self):
        self.live = None
        self._run_future = None
        self.sing_prefix = ""

    def start(self):
        if self._run_future and not self._run_future.done():
            return
        self._run_future = async_worker.submit(self._start_and_run_client())

    async def _start_and_run_client(self):
        try:
            await async_worker.init_db()
            config = await Db.get_dy_config()
            if not config or not config.room_id:
                webview.logger.info("Douyin room_id not configured, skipping.")
                return

            self.sing_prefix = config.sing_prefix
            self.live = DouyinLiveWebFetcher(live_id=config.room_id)
            self.live.on("danmu")(self.add_dydanmu)

            webview.logger.info("Douyin live client starting.")
            await async_worker.run_blocking(self.live.start)
        except Exception as e:
            webview.logger.error(f"Douyin task failed: {e}")
        finally:
            webview.logger.info("Douyin live client stopped.")

    def stop(self):
        if self.live:
            self.live.stop()
        if self._run_future:
            self._run_future.cancel()

    def add_dydanmu(self, danmu):
        content = danmu.get("content", "")
        if content.startswith(self.sing_prefix):
            song_name = content.replace(self.sing_prefix, "").strip()
            DdanmuList.append({"uid": danmu.get("user_id"), "uname": danmu.get("user_name"), "msg": song_name, "send_time": int(time.time()), "source": "douyin"})


bili_manager = Bili()
dy_manager = Douyin()


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
