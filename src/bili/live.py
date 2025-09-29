import time
from bilibili_api import live, sync
from src.utils import Decorator, logger, DanmuInfo


class MyLive(Decorator):
    room: live.LiveDanmaku
    song_prefix: str

    def __init__(self, room_id: int, credentials=None, song_prefix: str = "点歌"):
        self.room = live.LiveDanmaku(room_display_id=room_id, credential=credentials, max_retry=99)
        self.song_prefix = song_prefix

    def start(self):
        """
        Connect to the bilibili live room and start listening to danmaku

        This method will connect to the live room and start listening to danmaku.
        When a danmaku is received, it will be parsed and passed to the event handler
        "danmu" with the following info dict:
        {
            "uid": int,  # The user id of the user who sent the danmaku
            "uname": str,  # The username of the user who sent the danmaku
            "msg": str,  # The content of the danmaku
            "send_time": int  # The timestamp when the danmaku is sent
        }
        """
        self.room.on("DANMU_MSG")(self.on_danmu_msg)
        self.room.on("SUPER_CHAT_MESSAGE")(self.on_super_chat)

        sync(self.room.connect())

    def stop(self):
        """
        Disconnect from the bilibili live room

        This method will disconnect from the live room, and stop listening to danmaku
        """
        self.remove_all_listener()
        self.room.remove_all_event_listener()
        sync(self.room.disconnect())

    async def on_danmu_msg(self, event):
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
        if not msg.startswith(self.song_prefix):
            return

        song_name = msg.replace(self.song_prefix, "").strip()
        logger.info(song_name)
        danmu_info: DanmuInfo = {
            "uid": uid,
            "uname": uname,
            "msg": song_name,
            "medal_level": medal_level,
            "medal_name": medal_name,
            "guard_level": guard_level,
            "send_time": now
        }

        self.dispatch("danmu", danmu_info)

    async def on_super_chat(self, event):
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
        if not message.startswith(self.song_prefix):
            return
        song_name = message.replace(self.song_prefix, "").strip()
        logger.info(song_name)
        sc_info: DanmuInfo = {
            "uid": uid,
            "uname": uname,
            "msg": song_name,
            "medal_level": medal_level,
            "medal_name": medal_name,
            "guard_level": guard_level,
            "price": price,
            "send_time": int(time.time())
        }

        self.dispatch("sc", sc_info)
