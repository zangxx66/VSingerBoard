import asyncio
import threading
from typing import Coroutine, Callable, Any

from src.database import Db

# 定义回调函数的类型签名
DoneCallback = Callable[[Any], None]
FailCallback = Callable[[Exception], None]


class AsyncWorker:
    """
    在专用后台线程中运行一个持久的 asyncio 事件循环的单例工作者。
    提供线程安全的方法来提交协程到该循环中执行。
    """

    def __init__(self):
        self._loop = None
        self._thread = None
        self._ready = threading.Event()  # 用于发信号通知循环已准备就绪

    def start(self):
        """启动后台线程和事件循环。"""
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True, name="AsyncWorkerThread")
        self._thread.start()
        self._ready.wait()  # 等待直到循环启动并准备就绪

    def _run(self):
        """后台线程的主函数。"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # 在此循环中初始化数据库，然后再开始永久运行
        self._loop.run_until_complete(Db.init())

        self._ready.set()  # 发信号通知循环已准备好
        self._loop.run_forever()  # 运行循环直到 stop() 被调用

        # 循环停止后的清理工作
        tasks = asyncio.all_tasks(loop=self._loop)
        for task in tasks:
            task.cancel()
        group = asyncio.gather(*tasks, return_exceptions=True)
        self._loop.run_until_complete(group)
        self._loop.close()

    def stop(self):
        """停止后台事件循环和线程。"""
        if self._thread is None:
            return

        # 从另一个线程安全地停止循环
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()
        self._thread = None
        self._loop = None

    def submit(self, coro: Coroutine, on_done: DoneCallback = None, on_fail: FailCallback = None) -> asyncio.Future:
        """将一个协程提交到工作者的事件循环上运行。"""
        if self._loop is None or not self._loop.is_running():
            raise RuntimeError("AsyncWorker is not running.")

        future = asyncio.run_coroutine_threadsafe(coro, self._loop)

        if on_done or on_fail:
            def callback(fut):
                try:
                    result = fut.result()
                    if on_done:
                        on_done(result)
                except Exception as e:
                    if on_fail:
                        on_fail(e)

            future.add_done_callback(callback)

        return future

    async def run_db_operation(self, coro: Coroutine) -> Any:
        """
        在工作者循环中运行一个协程并等待其结果。
        此方法主要用于从外部异步上下文（如FastAPI）桥接到工作循环。
        """
        # 如果当前就在工作循环中，直接 await 即可
        try:
            if asyncio.get_running_loop() is self._loop:
                return await coro
        except RuntimeError:
            # 如果当前线程没有正在运行的循环，也会抛出 RuntimeError
            pass

        # 如果在不同的循环或线程中，则安全地提交并等待结果
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return await asyncio.to_thread(future.result)  # 异步地等待 concurrent.futures.Future 的结果

    def run_sync(self, coro: Coroutine) -> Any:
        """
        同步执行一个异步方法并返回结果。

        这个方法会阻塞当前线程直到异步方法执行完毕。

        :param coro: 要执行的协程
        :return: 协程的返回值
        """
        if self._loop is None or not self._loop.is_running():
            raise RuntimeError("AsyncWorker is not running.")

        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        # 等待 future 完成并获取结果，这将阻塞当前线程
        return future.result()


# 创建全局单例
async_worker = AsyncWorker()
