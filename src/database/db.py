from tortoise import Tortoise
from tortoise.connection import connections
from tortoise.exceptions import DBConnectionError
from .model import BiliConfig, BiliCredential, DyConfig, GloalConfig
from src.utils import get_path, logger


class Db:
    _initialized = False

    @classmethod
    async def init(cls):
        """
        Initialize database connection.
        This method should be idempotent and only called from a single asyncio event loop.
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
        Close all database connections.
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
    async def add_bconfig(cls, **kwargs):
        if not await BiliConfig.add(**kwargs):
            return False
        return True

    @classmethod
    async def update_bconfig(cls, pk, **kwargs):
        res = await BiliConfig.get(id=pk).update(**kwargs)
        return res

    @classmethod
    async def get_bconfig(cls, **kwargs):
        res = await BiliConfig.get(**kwargs).first()
        return res

    @classmethod
    async def get_dy_config(cls, **kwargs):
        res = await DyConfig.get(**kwargs).first()
        return res

    @classmethod
    async def update_dy_config(cls, pk, **kwargs):
        res = await DyConfig.get(id=pk).update(**kwargs)
        return res

    @classmethod
    async def add_dy_config(cls, **kwargs):
        if not await DyConfig.add(**kwargs):
            return False
        return True

    @classmethod
    async def add_gloal_config(cls, **kwargs):
        if not await GloalConfig.add(**kwargs):
            return False
        return True

    @classmethod
    async def update_gloal_config(cls, pk, **kwargs):
        res = await GloalConfig.get(id=pk).update(**kwargs)
        return res

    @classmethod
    async def get_gloal_config(cls, **kwargs):
        res = await GloalConfig.get(**kwargs).first()
        return res
