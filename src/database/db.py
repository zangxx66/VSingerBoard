from tortoise import Tortoise
from tortoise.connection import connections
from tortoise.backends.base.client import BaseDBAsyncClient
from .model import BiliConfig, BiliCredential, Subscribe
from src.utils import get_path


class Db:
    conn: BaseDBAsyncClient

    @classmethod
    async def init(cls):
        """
        Initialize database connection.

        :return: None
        """

        config = {
            "connections": {"default": f"sqlite://{get_path("vsingerboard.sqlite3", dir_name="data")}"},
            "apps": {
                "1.0": {
                    "models": ["database.model"],
                    "default_connection": "default"
                }
            }
        }

        await Tortoise.init(config=config)
        await Tortoise.generate_schemas()
        cls.conn = Tortoise.get_connection("default")

    @classmethod
    async def disconnect(cls):
        """
        Close all database connections.

        :return: None
        """
        await connections.close_all()

    @classmethod
    async def add_sub(cls, **kwargs):
        """
        Add a subscription.

        :param kwargs: Keyword arguments passed to Subscribe.add()
        :return: True if the subscription is added successfully, False otherwise
        """
        if not await Subscribe.add(**kwargs):
            return False
        return True

    @classmethod
    async def update_sub(cls, pk, **kwargs):
        """
        Update a subscription.

        :param pk: Primary key of the subscription to be updated
        :param kwargs: Keyword arguments passed to Subscribe.update()
        :return: The result of the update operation
        """
        res = await Subscribe.get(id=pk).update(**kwargs)
        return res

    @classmethod
    async def get_sub(cls, **kwargs):
        """
        Get subscriptions.

        :param kwargs: Keyword arguments passed to Subscribe.get()
        :return: The result of the get operation
        """
        res = await Subscribe.get(**kwargs)
        return res

    @classmethod
    async def add_bcredential(cls, **kwargs):
        """
        Add a BiliCredential.

        :param kwargs: Keyword arguments passed to BiliCredential.add()
        :return: True if the credential is added successfully, False otherwise
        """
        if not await BiliCredential.add(**kwargs):
            return False
        return True

    @classmethod
    async def update_bcredential(cls, pk, **kwargs):
        """
        Update a BiliCredential.

        :param pk: Primary key of the credential to be updated
        :param kwargs: Keyword arguments passed to BiliCredential.update()
        :return: The result of the update operation
        """
        res = await BiliCredential.get(id=pk).update(**kwargs)
        return res

    @classmethod
    async def delete_bcredential(cls, pk):
        """
        Delete a BiliCredential by its primary key.

        :param pk: Primary key of the credential to be deleted
        :return: The result of the delete operation
        """
        res = await BiliCredential.delete(id=pk)
        return res

    @classmethod
    async def get_bcredential_list(cls, **kwargs):
        """
        Get a list of BiliCredentials.

        :param kwargs: Keyword arguments passed to BiliCredential.get()
        :return: The result of the get operation
        """
        res = await BiliCredential.get(**kwargs)
        return res

    @classmethod
    async def get_bcredential(cls, **kwargs):
        """
        Get a BiliCredential by its primary key.

        :param pk: Primary key of the credential to be retrieved
        :return: The result of the get operation
        """
        res = await BiliCredential.get(**kwargs).first()
        return res

    @classmethod
    async def add_bconfig(cls, **kwargs):
        """
        Add a BiliConfig.

        :param kwargs: Keyword arguments passed to BiliConfig.add()
        :return: True if the config is added successfully, False otherwise
        """
        if not await BiliConfig.add(**kwargs):
            return False
        return True

    @classmethod
    async def update_bconfig(cls, pk, **kwargs):
        """
        Update a BiliConfig by its primary key.

        :param pk: Primary key of the config to be updated
        :param kwargs: Keyword arguments passed to BiliConfig.update()
        :return: The result of the update operation
        """
        res = await BiliConfig.get(id=pk).update(**kwargs)
        return res

    @classmethod
    async def get_bconfig(cls, **kwargs):
        """
        Get a BiliConfig by its keyword arguments.

        :param kwargs: Keyword arguments passed to BiliConfig.get()
        :return: The result of the get operation
        """
        res = await BiliConfig.get(**kwargs).first()
        return res
