import webview
from .live import MyLive, DanmuInfo
from src.database import Db as conn
from bilibili_api import Credential

danmuList: list[DanmuInfo] = []
live: MyLive = None


def add_danmu(danmu: DanmuInfo):
    danmuList.append(danmu)


class Api:
    def get_danmu(self):
        if len(danmuList) > 0:
            result = danmuList.copy()
            danmuList.clear()
            return result

    def get_width(self):
        # 系统分辨率
        screens = webview.screens
        screens = screens[0]
        width = screens.width
        return width


async def init_live():
    global live
    config = await conn.get_bconfig()
    if not config:
        return
    if config.room_id == 0:
        return
    bili_credential = await conn.get_bcredential(enable=True)
    credential: Credential = None
    if bili_credential is not None:
        credential = Credential(
            sessdata=bili_credential.sessdata,
            bili_jct=bili_credential.bili_jct,
            buvid3=bili_credential.buvid3,
            buvid4=bili_credential.buvid4,
            dedeuserid=bili_credential.dedeuserid,
            ac_time_value=bili_credential.ac_time_value
        )
    live = MyLive(room_id=config.room_id, credentials=credential, song_prefix=config.sing_prefix)
    live.on("danmu")(add_danmu)
    live.on("sc")(add_danmu)
    live.start()


async def restart_live():
    global live
    if live is not None:
        live.stop()
    await init_live()
