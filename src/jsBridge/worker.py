import asyncio
import threading
from src.database import Db


class AsyncWorker:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="async_worker")
        self._db_init_task = None
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def run_blocking(self, func, *args):
        return self._loop.run_in_executor(None, func, *args)

    async def init_db(self):
        if self._db_init_task and not self._db_init_task.done():
            await self._db_init_task
            return
        if Db._initialized:
            return

        self._db_init_task = self._loop.create_task(Db.init())
        await self._db_init_task

    async def disconnect_db(self):
        await Db.disconnect()


async_worker = AsyncWorker()
