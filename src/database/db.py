from tortoise import Tortoise
from tortoise.connection import connections
from .model import BiliConfig, BiliCredential, DyConfig, GloalConfig, SongHistory
from src.utils import get_path, logger


class Db:
    _initialized = False

    @classmethod
    async def init(cls):
        """
        初始化database连接

        此方法应具有幂等性，并且只能从单个 asyncio 事件循环中调用。
        """
        if cls._initialized:
            return

        try:
            config = {
                "connections": {"default": f"sqlite://{get_path('vsingerboard.sqlite3', dir_name='data')}"},
                "apps": {
                    "1.0": {
                        "models": ["src.database.model"],
                        "default_connection": "default"
                    }
                }
            }

            await Tortoise.init(config=config)
            await Tortoise.generate_schemas()
            cls._initialized = True
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.exception(f"Database initialization failed: {e}")
            raise

    @classmethod
    async def disconnect(cls):
        """
       关闭所有database连接
        """
        if not cls._initialized:
            return
        await connections.close_all()
        cls._initialized = False
        logger.info("Database disconnected.")

    @classmethod
    async def add_bcredential(cls, **kwargs):
        if not await BiliCredential.add(**kwargs):
            return False
        return True

    @classmethod
    async def update_bcredential(cls, pk, **kwargs):
        res = await BiliCredential.get(id=pk).update(**kwargs)
        return res

    @classmethod
    async def delete_bcredential(cls, pk):
        res = await BiliCredential.delete(id=pk)
        return res

    @classmethod
    async def get_bcredential_list(cls, **kwargs):
        res = await BiliCredential.get(**kwargs)
        return res

    @classmethod
    async def get_bcredential(cls, **kwargs):
        res = await BiliCredential.get(**kwargs).first()
        return res

    @classmethod
    async def add_or_update_bili_config(cls, **kwargs):
        id = kwargs.get("id")
        del kwargs["id"]
        bconfig = await BiliConfig.get(id=id).first()
        try:
            if bconfig:
                await bconfig.get(id=id).update(**kwargs)
                return bconfig.id
            else:
                bconfig = await BiliConfig.create(**kwargs)
                return bconfig.id
        except Exception as e:
            logger.error(f"add_or_update_bili_config error: {e}")
            return 0

    @classmethod
    async def get_bconfig(cls, **kwargs):
        res = await BiliConfig.get(**kwargs).first()
        return res

    @classmethod
    async def get_dy_config(cls, **kwargs):
        res = await DyConfig.get(**kwargs).first()
        return res

    @classmethod
    async def add_or_updae_dy_config(cls, **kwargs):
        id = kwargs.get("id")
        del kwargs["id"]
        dy_config = await DyConfig.get(id=id).first()
        try:
            if dy_config:
                await dy_config.get(id=id).update(**kwargs)
                return dy_config.id
            else:
                dy_config = await DyConfig.create(**kwargs)
                return dy_config.id
        except Exception as e:
            logger.error(f"add_or_update_dy_config error: {e}")
            return 0

    @classmethod
    async def get_gloal_config(cls, **kwargs):
        res = await GloalConfig.get(**kwargs).first()
        return res

    @classmethod
    async def add_or_update_gloal_config(cls, **kwargs):
        id = kwargs.get("id")
        del kwargs["id"]
        gloal_config = await GloalConfig.get(id=id).first()
        try:
            if gloal_config:
                await gloal_config.get(id=id).update(**kwargs)
                return gloal_config.id
            else:
                gloal_config = await GloalConfig.create(**kwargs)
                return gloal_config.id
        except Exception as e:
            logger.error(f"add_or_update_gloal_config error: {e}")
            return 0

    @classmethod
    async def get_song_history(cls, uid: int, source: str):
        res = await SongHistory.get(uid=uid, source=source).order_by("-create_time").first()
        return res

    @classmethod
    async def add_song_history(cls, **kwargs):
        res = await SongHistory.create(**kwargs)
        return res

    @classmethod
    async def get_song_history_page(cls,
                                    uname: str = None,
                                    song_name: str = None,
                                    source: str = None,
                                    start_time: int = 0,
                                    end_time: int = 0,
                                    page: int = 1,
                                    size: int = 20):
        query = SongHistory.all()
        if uname:
            query = query.filter(uname__icontains=uname)
        if song_name:
            query = query.filter(song_name__icontains=song_name)
        if source:
            query = query.filter(source__icontains=source)
        if start_time:
            query = query.filter(create_time__gte=start_time)
        if end_time:
            query = query.filter(create_time__lte=end_time)

        total = await query.count()
        songs = await query.offset((page - 1) * size).limit(size).order_by("-create_time").all()

        return total, songs
