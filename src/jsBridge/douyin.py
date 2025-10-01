import time
from .worker import async_worker
from src.database import Db
from src.douyin import DouyinLiveWebFetcher
from src.utils import logger, DanmuInfo


class Douyin:
    def __init__(self):
        self.live = None
        self._run_future = None
        self.danmus: list[DanmuInfo] = []
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
                logger.info("Douyin room_id not configured, skipping.")
                return

            self.sing_prefix = config.sing_prefix
            self.live = DouyinLiveWebFetcher(live_id=config.room_id)
            self.live.on("danmu")(self.add_dydanmu)

            logger.info("Douyin live client starting.")
            await async_worker.run_blocking(self.live.start)
        except Exception as e:
            logger.error(f"Douyin task failed: {e}")
        finally:
            logger.info("Douyin live client stopped.")

    def stop(self):
        if self.live:
            self.live.remove_listener("danmu", self.add_dydanmu)
            self.live.stop()
        if self._run_future:
            self._run_future.cancel()

    def get_status(self):
        if self.live:
            return 1 if self.live.ws_connect_status else 0
        else:
            return -1

    def get_list(self):
        if len(self.danmus) == 0:
            return None
        result = self.danmus.copy()
        self.danmus.clear()
        return result

    def add_dydanmu(self, danmu):
        content = danmu.get("content", "")
        if content.startswith(self.sing_prefix):
            song_name = content.replace(self.sing_prefix, "", 1).strip()
            danmu_info: DanmuInfo = {
                "uid": danmu.get("user_id"),
                "uname": danmu.get("user_name"),
                "msg": song_name,
                "send_time": int(time.time()),
                "source": "douyin"
            }
            self.danmus.append(danmu_info)
