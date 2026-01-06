import time
import asyncio
from src.utils import logger, DanmuInfo, async_worker, send_notification
from src.database import Db
from src.manager import subscribe_manager
from bilibili_api import live, Credential


class Bili:
    def __init__(self):
        self._stop_event = asyncio.Event()
        self._run_future = None
        self.live = None
        self.danmus: list[DanmuInfo] = []
        self.del_list = []
        self.config = None
        self.credential = None

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
                    self.config = config
                logger.info("Bilibili room_id not configured, skipping.")
                return

            self.config = config
            self.credential = await Db.get_bcredential(enable=True)
            if self.credential:
                credential = Credential(
                    sessdata=self.credential.sessdata,
                    bili_jct=self.credential.bili_jct,
                    buvid3=self.credential.buvid3,
                    buvid4=self.credential.buvid4,
                    dedeuserid=self.credential.dedeuserid,
                    ac_time_value=self.credential.ac_time_value
                )
            else:
                credential = None

            self.live = live.LiveDanmaku(room_display_id=self.config.room_id, credential=credential, max_retry=99)
            self.live.on("DANMU_MSG")(self.on_msg)
            self.live.on("SUPER_CHAT_MESSAGE")(self.on_sc)
            subscribe_manager.add_job("interval", minutes=30, id="refresh_credential", replace_existing=True)(self.refresh_credential)

            await self.live.connect()
            logger.info("Bilibili live client starting.")
            await self._stop_event.wait()
        except asyncio.CancelledError:
            logger.warning("Bilibili main task was cancelled.")
        except Exception as e:
            logger.error(f"Bilibili task failed: {e}")
        finally:
            if self.live:
                try:
                    await self.live.disconnect()
                except Exception as e:
                    logger.error(f"Bilibili disconnect failed when trying to disconnect: {e}")
                self.live.remove_event_listener("DANMU_MSG", self.on_msg)
                self.live.remove_event_listener("SUPER_CHAT_MESSAGE", self.on_sc)
                self.live = None
                self.credential = None
            logger.info("Bilibili live client stopped.")

    async def stop(self):
        subscribe_manager.cancel_subscribe("refresh_credential")
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

    async def restart(self):
        await self.stop()
        await asyncio.sleep(1)
        self.start()

    def get_status(self):
        if self.live:
            return self.live.get_status()
        else:
            return -1

    def get_list(self):
        if len(self.danmus) == 0:
            return []
        result = self.danmus.copy()
        self.danmus.clear()
        return result

    def get_del_list(self):
        if len(self.del_list) == 0:
            return []
        result = self.del_list.copy()
        self.del_list.clear()
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
        if msg.startswith("取消点歌"):
            cancel_song = msg.replace("取消点歌", "", 1).strip()
            history = await Db.get_song_history(uid=uid, source="bilibili")
            if history:
                self.del_list.append({"msg_id": history.id, "uid": uid, "uname": uname, "song_name": cancel_song})
            return
        if not msg.startswith(self.config.sing_prefix):
            return
        if self.config.modal_level > 0 and medal_level < self.config.modal_level:
            return
        if self.config.user_level > 0 and guard_level > self.config.user_level:
            return
        if self.config.sing_cd > 0:
            history = await Db.get_song_history(uid=uid, source="bilibili")
            if history and (now - history.create_time) / 1000 < self.config.sing_cd:
                return

        song_name = msg.replace(self.config.sing_prefix, "", 1).strip()
        logger.info(song_name)

        history = await Db.add_song_history(uid=uid, uname=uname, song_name=song_name, source="bilibili", create_time=now)

        danmu_info: DanmuInfo = {
            "msg_id": history.id,
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
        now = int(time.time())
        medal_level = 0
        medal_name = ""
        guard_level = 0
        if sc_data["medal_info"] is not None:
            guard_level = sc_data["medal_info"]["guard_level"]
            medal_level = sc_data["medal_info"]["medal_level"]
            medal_name = sc_data["medal_info"]["medal_name"]

        logger.debug(f"[{medal_name} {medal_level}]:{uname}:{message}")
        if not message.startswith(self.config.sing_prefix):
            return
        if self.config.modal_level > 0 and medal_level < self.config.modal_level:
            return
        if self.config.user_level > 0 and guard_level > self.config.user_level:
            return
        if self.config.sing_cd > 0:
            history = await Db.get_song_history(uid=uid, source="bilibili")
            if history and (now - history.create_time) / 1000 < self.config.sing_cd:
                return

        song_name = message.replace(self.config.sing_prefix, "", 1).strip()
        logger.info(song_name)

        song_info = await Db.get_playlist(song_name=song_name)
        if song_info:
            if song_info.is_sc and price < song_info.sc_price:
                return

        history = await Db.add_song_history(uid=uid, uname=uname, song_name=song_name, source="bilibili", create_time=now)

        sc_info: DanmuInfo = {
            "msg_id": history.id,
            "uid": uid,
            "uname": uname,
            "msg": song_name,
            "medal_level": medal_level,
            "medal_name": medal_name,
            "guard_level": guard_level,
            "price": price,
            "send_time": now,
            "source": "bilibili"
        }
        self.danmus.append(sc_info)

        config = await Db.get_gloal_config()
        if not config or not config.notification:
            return

        send_notification("收到新的点歌", song_name)

    async def refresh_credential(self):
        if not self.credential:
            return
        credential = Credential(
            sessdata=self.credential.sessdata,
            bili_jct=self.credential.bili_jct,
            buvid3=self.credential.buvid3,
            buvid4=self.credential.buvid4,
            dedeuserid=self.credential.dedeuserid,
            ac_time_value=self.credential.ac_time_value
        )
        if await credential.check_valid():
            if await credential.check_refresh():
                await credential.refresh()
                data_dic = credential.__dict__
                model_fileds = ['ac_time_value', 'bili_jct', 'buvid3', 'buvid4', 'dedeuserid', 'sessdata']
                new_dic = {k: v for k, v in data_dic.items() if v is not None and k in model_fileds}
                await Db.update_bcredential(pk=self.credential.id, **new_dic)
                logger.info("refresh credential!")
        logger.info("exec refresh_credential job")


bili_manager = Bili()
