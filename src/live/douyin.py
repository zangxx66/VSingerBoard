import time
import asyncio
from src.database import Db
from src.douyin import DouyinLiveWebFetcher
from src.utils import logger, DanmuInfo, async_worker, send_notification


class Douyin:
    def __init__(self):
        self._run_future = None
        self._stop_event = asyncio.Event()
        self.live = None
        self.danmus: list[DanmuInfo] = []
        self.sing_prefix = ""
        self.room_id = 0
        self.sing_cd = 0
        self.fans_level = 0

    def start(self):
        if self._run_future and not self._run_future.done():
            return
        self._stop_event.clear()
        self._run_future = async_worker.submit(self._main())
        logger.info("Douyin main task submitted to worker.")

    async def _main(self):
        self.live = None
        try:
            config = await Db.get_dy_config()
            if not config or config.room_id == 0:
                if config:
                    self.room_id = config.room_id
                logger.info("Douyin room_id not configured, skipping.")
                return

            self.sing_prefix = config.sing_prefix
            self.room_id = config.room_id
            self.sing_cd = config.sing_cd
            self.fans_level = config.fans_level
            self.live = DouyinLiveWebFetcher(live_id=self.room_id, max_retries=99)
            self.live.on("danmu")(self.add_dydanmu)

            await self.live.connect_async()
            logger.info("Douyin live client connected.")

            await self._stop_event.wait()

        except asyncio.CancelledError:
            logger.warning("Douyin main task was cancelled.")
        except Exception as e:
            logger.error(f"Douyin main task failed: {e}")
        finally:
            logger.info("Douyin live client stopping.")
            if self.live:
                await self.live.disconnect_async()
                self.live.remove_listener("danmu", self.add_dydanmu)
                self.live = None
            logger.info("Douyin live client stopped.")

    async def stop(self):
        if self._run_future and not self._run_future.done():
            logger.info("Stopping Douyin main task.")
            self._stop_event.set()
            try:
                awaitable_future = asyncio.wrap_future(self._run_future)
                await asyncio.wait_for(awaitable_future, timeout=5)
            except asyncio.TimeoutError:
                logger.error("【X】Timed out waiting for Douyin task to stop.")
                self._run_future.cancel()
            except Exception as e:
                logger.error(f"Error waiting for Douyin task to stop: {e}")
            logger.info("Douyin main task stopped.")

        self._run_future = None

    def get_status(self):
        if self.live:
            return self.live.ws_connect_status
        else:
            return -1

    def get_list(self):
        if len(self.danmus) == 0:
            return []
        result = self.danmus.copy()
        self.danmus.clear()
        return result

    async def add_dydanmu(self, danmu):
        content = danmu.get("content", "")
        uid = danmu.get("user_id")
        fans_club_data = danmu.get("fans_club_data")
        medal_level = 0
        medal_name = ""
        guard_level = 0
        now = int(time.time())
        if "level" in fans_club_data:
            medal_level = fans_club_data["level"]
        if "club_name" in fans_club_data:
            medal_name = fans_club_data["club_name"]

        if not content.startswith(self.sing_prefix):
            return
        if self.fans_level > 0 and medal_level < self.fans_level:
            return
        if self.sing_cd > 0:
            history = await Db.get_song_history(uid=uid, source="douyin")
            if history and (now - history.create_time) / 1000 < self.sing_cd:
                return

        song_name = content.replace(self.sing_prefix, "", 1).strip()
        logger.info(song_name)

        danmu_info: DanmuInfo = {
            "uid": uid,
            "uname": danmu.get("user_name"),
            "msg": song_name,
            "send_time": now,
            "source": "douyin",
            "guard_level": guard_level,
            "medal_level": medal_level,
            "medal_name": medal_name,
        }
        self.danmus.append(danmu_info)

        await Db.add_song_history(uid=uid, song_name=song_name, source="douyin", create_time=now)

        config = await Db.get_gloal_config()
        if not config or not config.notification:
            return

        send_notification("收到新的点歌", song_name)


douyin_manager = Douyin()
