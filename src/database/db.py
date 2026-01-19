import os
import uuid
from tortoise import Tortoise
from tortoise.connection import connections
from tortoise.models import Q
from aerich import Command
from .model import BiliConfig, BiliCredential, DyConfig, GloalConfig, SongHistory, Playlist
from src.utils import get_path, logger, get_support_dir, __version__ as CURRENT_VERSION

MIGRATIONS_LOCATION = os.path.join(get_support_dir(), "migrations")
TORTISE_ORM = {
    "connections": {"default": f"sqlite://{get_path('vsingerboard.sqlite3', dir_name='data')}"},
    "apps": {
        CURRENT_VERSION: {
            "models": ["src.database.model", "aerich.models"],
            "default_connection": "default",
        }
    }
}


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
            await cls.run_db_upgrade(cls)
            await Tortoise.init(config=TORTISE_ORM)
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

    async def run_db_upgrade(cls):
        """
        更新database

        """
        try:
            async with Command(tortoise_config=TORTISE_ORM, app=CURRENT_VERSION, location=MIGRATIONS_LOCATION) as command:
                await command.init()
                conn = Tortoise.get_connection("default")
                _, has_aerich = await conn.execute_query("select count(1) as count from sqlite_master where type='table' and name='aerich';")
                _, has_migrate = await conn.execute_query(f"select exists(select 1 from aerich where app='{CURRENT_VERSION}') as result;")
                if has_aerich[0]["count"] == 0 or has_migrate[0]["result"] == 0:
                    logger.info("Initializing aerich for the first time...")
                    await command.init_db(safe=True)
                    logger.info("Aerich initialized.")
                logger.info("Starting database schema upgrade...")
                # Use a unique name to avoid collisions
                await command.migrate(f"auto_{uuid.uuid4().hex[:12]}")
                await command.upgrade()
                logger.info("Database schema upgrade finished.")
        except Exception as ex:
            raise logger.exception(ex)

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

    @classmethod
    async def get_playlist_page(cls, keyword: str = None, page: int = 1, size: int = 20):
        query = Playlist.all()
        if keyword:
            query = query.filter(Q(song_name__icontains=keyword, tag__icontains=keyword, singer__icontains=keyword, language__icontains=keyword, join_type="OR"))

        total = await query.count()
        rows = await query.offset((page - 1) * size).limit(size).order_by("-create_time").all()

        return total, rows

    @classmethod
    async def get_playlist(cls, **kwargs):
        result = await Playlist.filter(**kwargs).first()
        return result

    @classmethod
    async def delete_playlist(cls, ids: list[int]):
        result = await Playlist.filter(id__in=ids).delete()
        return result

    @classmethod
    async def add_or_update_playlist(cls, **kwargs):
        id = kwargs.get("id")
        del kwargs["id"]
        playlist = await Playlist.get(id=id).first()
        try:
            if playlist:
                await Playlist.get(id=id).update(**kwargs)
                return playlist.id
            else:
                playlist = await Playlist.create(**kwargs)
                return playlist.id
        except Exception as e:
            logger.error(f"add_or_update_playlist error: {e}")
            return 0

    @classmethod
    async def bulk_add_playlist(cls, params: list[dict[str, any]]):
        objects: list[Playlist] = []
        for item in params:
            obj = Playlist(**item)
            objects.append(obj)
        await Playlist.bulk_create(objects, batch_size=500)
