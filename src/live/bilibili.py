import time
import asyncio
from src.utils import logger, DanmuInfo, async_worker, send_notification
from src.database import Db
from bilibili_api import live, Credential


class Bili:
    def __init__(self):
        self._stop_event = asyncio.Event()
        self._run_future = None
        self.live = None
        self.danmus: list[DanmuInfo] = []
        self.sing_prefix = ""
        self.room_id = 0

    def start(self):
        if self._run_future and not self._run_future.done():
            return
        self._stop_event.clear()
        self._run_future = async_worker.submit(self._start_and_run_client())
        logger.info("Bilibili main task submitted to worker.")

    async def _start_and_run_client(self):
        self.live = None
        try:
            config = await Db.get_bconfig()
            if not config or config.room_id == 0:
                if config:
                    self.room_id = config.room_id
                logger.info("Bilibili room_id not configured, skipping.")
                return

            self.sing_prefix = config.sing_prefix
            self.room_id = config.room_id
            bili_credential = await Db.get_bcredential(enable=True)
            credential = Credential(**bili_credential.__dict__) if bili_credential else None

            self.live = live.LiveDanmaku(room_display_id=self.room_id, credential=credential, max_retry=99)
            self.live.on("DANMU_MSG")(self.on_msg)
            self.live.on("SUPER_CHAT_MESSAGE")(self.on_sc)

            await self.live.connect()
            logger.info("Bilibili live client starting.")
            await self._stop_event.wait()
        except asyncio.CancelledError:
            logger.info("Bilibili main task was cancelled.")
        except Exception as e:
            logger.error(f"Bilibili task failed: {e}")
        finally:
            if self.live:
                await self.live.disconnect()
                self.live.remove_event_listener("DANMU_MSG", self.on_msg)
                self.live.remove_event_listener("SUPER_CHAT_MESSAGE", self.on_sc)
                self.live = None
            logger.info("Bilibili live client stopped.")

    async def stop(self):
        if self._run_future and not self._run_future.done():
            logger.info("Stopping Bilibili main task.")
            self._stop_event.set()
            try:
                awaitable_future = asyncio.wrap_future(self._run_future)
                await asyncio.wait_for(awaitable_future, timeout=5)
            except asyncio.TimeoutError:
                logger.error("【X】Timed out waiting for Bilibili task to stop.")
                self._run_future.cancel()
            except Exception as e:
                logger.error(f"Error waiting for Bilibili task to stop: {e}")
            logger.info("Bilibili main task stopped.")
        self._run_future = None

    def get_status(self):
        if self.live:
            return self.live.get_status()
        else:
            return -1

    def get_list(self):
        if len(self.danmus) == 0:
            return None
        result = self.danmus.copy()
        self.danmus.clear()
        return result

    async def on_msg(self, event):
        info = event["data"]["info"]
        msg = str(info[1])
        uid = info[2][0]
        uname = info[2][1]
        now = int(time.time())
        user_info = info[0][15]["user"]
        medal_level = 0
        medal_name = ""
        guard_level = 0
        if user_info["medal"] is not None:
            medal_level = user_info["medal"]["level"]
            medal_name = user_info["medal"]["name"]
            guard_level = user_info["medal"]["guard_level"]

        logger.debug(f"[{medal_name} {medal_level}]:{uname}:{msg}")
        if not msg.startswith(self.sing_prefix):
            return

        song_name = msg.replace(self.sing_prefix, "", 1).strip()
        logger.info(song_name)

        danmu_info: DanmuInfo = {
            "uid": uid,
            "uname": uname,
            "msg": song_name,
            "medal_level": medal_level,
            "medal_name": medal_name,
            "guard_level": guard_level,
            "send_time": now,
            "source": "bilibili"
        }
        self.danmus.append(danmu_info)

        config = await Db.get_gloal_config()
        if not config or not config.notification:
            return

        send_notification("收到新的点歌", song_name)

    async def on_sc(self, event):
        sc_data = event["data"]["data"]
        uname = sc_data["user_info"]["uname"]
        uid = sc_data["uid"]
        message = str(sc_data["message"])
        price = sc_data["price"]
        medal_level = 0
        medal_name = ""
        guard_level = 0
        if sc_data["medal_info"] is not None:
            guard_level = sc_data["medal_info"]["guard_level"]
            medal_level = sc_data["medal_info"]["medal_level"]
            medal_name = sc_data["medal_info"]["medal_name"]

        logger.debug(f"[{medal_name} {medal_level}]:{uname}:{message}")
        if not message.startswith(self.sing_prefix):
            return

        song_name = message.replace(self.sing_prefix, "", 1).strip()
        logger.info(song_name)

        sc_info: DanmuInfo = {
            "uid": uid,
            "uname": uname,
            "msg": song_name,
            "medal_level": medal_level,
            "medal_name": medal_name,
            "guard_level": guard_level,
            "price": price,
            "send_time": int(time.time()),
            "source": "bilibili"
        }
        self.danmus.append(sc_info)

        config = await Db.get_gloal_config()
        if not config or not config.notification:
            return

        send_notification("收到新的点歌", song_name)


bili_manager = Bili()
