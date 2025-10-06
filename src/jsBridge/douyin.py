import time
import asyncio
from src.database import Db
from src.douyin import DouyinLiveWebFetcher
from src.utils import logger, DanmuInfo, async_worker, send_notification


class Douyin:
    def __init__(self):
        self.live = None
        self._run_future = None
        self.danmus: list[DanmuInfo] = []
        self.sing_prefix = ""
        self._stop_event = asyncio.Event()

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
                logger.info("Douyin room_id not configured, skipping.")
                return

            self.sing_prefix = config.sing_prefix
            self.live = DouyinLiveWebFetcher(live_id=config.room_id, max_retries=99)
            self.live.on("danmu")(self.add_dydanmu)

            await self.live.connect_async()
            logger.info("Douyin live client connected.")

            await self._stop_event.wait()

        except asyncio.CancelledError:
            logger.info("Douyin main task was cancelled.")
        except Exception as e:
            logger.error(f"Douyin main task failed: {e}")
        finally:
            logger.info("Douyin live client stopping.")
            if self.live:
                await self.live.disconnect_async()
                self.live.remove_listener("danmu", self.add_dydanmu)
                self.live = None

    async def stop(self):
        if self._run_future and not self._run_future.done():
            logger.info("Stopping Douyin main task.")
            self._stop_event.set()
            try:
                awaitable_future = asyncio.wrap_future(self._run_future)
                await asyncio.wait_for(awaitable_future, timeout=15)
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
            return None
        result = self.danmus.copy()
        self.danmus.clear()
        return result

    async def add_dydanmu(self, danmu):
        content = danmu.get("content", "")
        if not content.startswith(self.sing_prefix):
            return

        song_name = content.replace(self.sing_prefix, "", 1).strip()
        logger.info(song_name)

        danmu_info: DanmuInfo = {
            "uid": danmu.get("user_id"),
            "uname": danmu.get("user_name"),
            "msg": song_name,
            "send_time": int(time.time()),
            "source": "douyin"
        }
        self.danmus.append(danmu_info)

        config = await Db.get_gloal_config()
        if not config or not config.notification:
            return

        send_notification("收到新的点歌", song_name)