import asyncio
from tortoise import Tortoise
from tortoise.connection import connections
from .model import BiliConfig, BiliCredential, DyConfig, GloalConfig
from src.utils import get_path, logger


class Db:

    def __init__(self):
        try:
            # Get the current running event loop.
            loop = asyncio.get_running_loop()
            # If a loop is running, create a task to run the init coroutine concurrently.
            loop.create_task(self.init())
        except RuntimeError:
            # If no event loop is running, a RuntimeError is raised.
            # In this case, run the init coroutine in a new event loop.
            asyncio.run(self.init())
        except Exception as e:
            logger.error(f"An unexpected error occurred during database initialization: {e}")

    # @classmethod
    async def init(cls):
        """
        Initialize database connection.

        :return: None
        """

        config = {
            "connections": {"default": f"sqlite://{get_path("vsingerboard.sqlite3", dir_name="data")}"},
            "apps": {
                "1.0": {
                    "models": ["src.database.model"],
                    "default_connection": "default"
                }
            }
        }

        await Tortoise.init(config=config)
        await Tortoise.generate_schemas()
        # cls.conn = Tortoise.get_connection("default")

    # @classmethod
    async def disconnect(cls):
        """
        Close all database connections.

        :return: None
        """
        await connections.close_all()

    # @classmethod
    async def add_bcredential(cls, **kwargs):
        """
        Add a BiliCredential.

        :param kwargs: Keyword arguments passed to BiliCredential.add()
        :return: True if the credential is added successfully, False otherwise
        """
        if not await BiliCredential.add(**kwargs):
            return False
        return True

    # @classmethod
    async def update_bcredential(cls, pk, **kwargs):
        """
        Update a BiliCredential.

        :param pk: Primary key of the credential to be updated
        :param kwargs: Keyword arguments passed to BiliCredential.update()
        :return: The result of the update operation
        """
        res = await BiliCredential.get(id=pk).update(**kwargs)
        return res

    # @classmethod
    async def delete_bcredential(cls, pk):
        """
        Delete a BiliCredential by its primary key.

        :param pk: Primary key of the credential to be deleted
        :return: The result of the delete operation
        """
        res = await BiliCredential.delete(id=pk)
        return res

    # @classmethod
    async def get_bcredential_list(cls, **kwargs):
        """
        Get a list of BiliCredentials.

        :param kwargs: Keyword arguments passed to BiliCredential.get()
        :return: The result of the get operation
        """
        res = await BiliCredential.get(**kwargs)
        return res

    # @classmethod
    async def get_bcredential(cls, **kwargs):
        """
        Get a BiliCredential by its primary key.

        :param pk: Primary key of the credential to be retrieved
        :return: The result of the get operation
        """
        res = await BiliCredential.get(**kwargs).first()
        return res

    # @classmethod
    async def add_bconfig(cls, **kwargs):
        """
        Add a BiliConfig.

        :param kwargs: Keyword arguments passed to BiliConfig.add()
        :return: True if the config is added successfully, False otherwise
        """
        if not await BiliConfig.add(**kwargs):
            return False
        return True

    # @classmethod
    async def update_bconfig(cls, pk, **kwargs):
        """
        Update a BiliConfig by its primary key.

        :param pk: Primary key of the config to be updated
        :param kwargs: Keyword arguments passed to BiliConfig.update()
        :return: The result of the update operation
        """
        res = await BiliConfig.get(id=pk).update(**kwargs)
        return res

    # @classmethod
    async def get_bconfig(cls, **kwargs):
        """
        Get a BiliConfig by its keyword arguments.

        :param kwargs: Keyword arguments passed to BiliConfig.get()
        :return: The result of the get operation
        """
        res = await BiliConfig.get(**kwargs).first()
        return res

    # @classmethod
    async def get_dy_config(cls, **kwargs):
        """
        Get a DyConfig by its keyword arguments.

        :param kwargs: Keyword arguments passed to DyConfig.get()
        :return: The result of the get operation
        """
        res = await DyConfig.get(**kwargs).first()
        return res

    # @classmethod
    async def update_dy_config(cls, pk, **kwargs):
        """
        Update a DyConfig by its primary key.

        :param pk: Primary key of the config to be updated
        :param kwargs: Keyword arguments passed to DyConfig.update()
        :return: The result of the update operation
        """
        res = await DyConfig.get(id=pk).update(**kwargs)
        return res

    # @classmethod
    async def add_dy_config(cls, **kwargs):
        """
        Add a DyConfig.

        :param kwargs: Keyword arguments passed to DyConfig.add()
        :return: True if the config is added successfully, False otherwise
        """
        if not await DyConfig.add(**kwargs):
            return False
        return True

    async def add_gloal_config(cls, **kwargs):
        """
        Add a GlobalConfig.

        :param kwargs: Keyword arguments passed to GlobalConfig.add()
        :return: True if the config is added successfully, False otherwise
        """
        if not await GloalConfig.add(**kwargs):
            return False
        return True

    async def update_gloal_config(cls, pk, **kwargs):
        """
        Update a GlobalConfig by its primary key.

        :param pk: Primary key of the config to be updated
        :param kwargs: Keyword arguments passed to GlobalConfig.update()
        :return: The result of the update operation
        """
        res = await GloalConfig.get(id=pk).update(**kwargs)
        return res

    async def get_gloal_config(cls, **kwargs):
        """
        Get a GlobalConfig by its keyword arguments.

        :param kwargs: Keyword arguments passed to GlobalConfig.get()
        :return: The result of the get operation
        """
        res = await GloalConfig.get(**kwargs).first()
        return res
