import asyncio
import threading
from src.database import Db


class AsyncWorker:
    """
    一个在后台线程中运行asyncio事件循环的辅助类。
    这允许在主同步线程中提交异步任务。
    """
    def __init__(self):
        """
        初始化AsyncWorker，创建一个新的事件循环和后台线程。
        """
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="async_worker")
        self._db_init_task = None
        self._thread.start()

    def _run_loop(self):
        """
        后台线程运行的目标方法。
        设置并永久运行事件循环。
        """
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro):
        """
        从任何线程向工作者的事件循环提交一个协程。
        这是一个线程安全的方法。

        :param coro: 要执行的协程。
        :return: 一个concurrent.futures.Future对象，可用于获取结果。
        """
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def run_blocking(self, func, *args):
        """
        在事件循环的执行器中运行一个阻塞函数（如普通函数）。
        这可以防止阻塞函数阻塞事件循环。

        :param func: 要运行的阻塞函数。
        :param args: 传递给函数的参数。
        :return: 一个Future对象。
        """
        return self._loop.run_in_executor(None, func, *args)

    async def init_db(self):
        """
        异步初始化数据库连接。
        如果初始化已在进行中或已完成，则不会重复执行。
        """
        if self._db_init_task and not self._db_init_task.done():
            await self._db_init_task
            return
        if Db._initialized:
            return

        self._db_init_task = self._loop.create_task(Db.init())
        await self._db_init_task

    async def disconnect_db(self):
        """
        异步断开数据库连接。
        """
        await Db.disconnect()

    async def run_db_operation(self, func):
        """
        在工作者线程中运行一个数据库操作，并等待其完成。

        :param func: 要作为数据库操作运行的异步函数。
        :return: 数据库操作的结果。
        """
        future = self.submit(func)
        return await asyncio.wrap_future(future)


# 全局AsyncWorker实例，方便在应用各处使用
async_worker = AsyncWorker()
"""
全局AsyncWorker实例，方便在应用各处使用
"""
