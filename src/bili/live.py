import time
from bilibili_api import live, sync
from typing import TypedDict, Optional
from src.utils import logger, Decorator


class DanmuInfo(TypedDict):
    uid: int
    uname: str
    msg: str
    medal_level: int
    medal_name: str
    guard_level: int
    price: Optional[int]
    send_time: int


class MyLive(Decorator):
    room: live.LiveDanmaku

    def __init__(self, room_id: int, credentials=None):
        self.room = live.LiveDanmaku(room_display_id=room_id, credential=credentials)

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

        sync(self.room.connect())

    def stop(self):
        """
        Disconnect from the bilibili live room

        This method will disconnect from the live room, and stop listening to danmaku
        """
        sync(self.room.disconnect())

    async def on_danmu_msg(self, event):
        info = event["data"]["info"]
        msg = info[1]
        uid = info[2][0]
        uname = info[2][1]
        now = int(time.time())
        user_info = info[0][15]["user"]
        medal_level = user_info["medal"]["level"]
        medal_name = user_info["medal"]["name"]
        guard_level = user_info["medal"]["guard_level"]

        logger.info(f"{uname}: {msg}")

        if not msg.startswith("点歌"):
            return

        danmu_info: DanmuInfo = {
            "uid": uid,
            "uname": uname,
            "msg": msg,
            "medal_level": medal_level,
            "medal_name": medal_name,
            "guard_level": guard_level,
            "send_time": now
        }

        self.dispatch("danmu", danmu_info)
