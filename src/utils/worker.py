import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Coroutine, Callable, Any


# 定义回调函数的类型签名
DoneCallback = Callable[[Any], None]
FailCallback = Callable[[Exception], None]


class AsyncWorker:
    """
    一个在线程池中执行异步任务的后台工作者。
    它支持两种任务模式：
    1. awaitable 模式 (run_db_operation): 异步等待任务结果返回。
    2. 回调模式 (submit): 提交任务后立即返回，通过回调函数处理结果。
    """

    def __init__(self, max_workers=10):
        """
        初始化 Worker，并自动提交数据库初始化任务。
        :param max_workers: 线程池的最大线程数。
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._is_running = True

    async def run_db_operation(self, coro: Coroutine) -> Any:
        """
        [awaitable] 在后台线程池中执行一个协程，并异步地返回结果。
        这个方法本身是异步的，可以被调用者 await。

        :param coro: 需要在后台执行的协程 (例如一个 tortoise-orm 的数据库操作)。
        :return: 协程的执行结果。
        """
        if not self._is_running:
            raise RuntimeError("工作者已停止运行。")

        main_loop = asyncio.get_running_loop()

        def run_coro_in_new_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        # 将 'run_coro_in_new_loop' 函数提交到线程池执行。
        # 这会返回一个 concurrent.futures.Future 对象。
        conc_future = self.executor.submit(run_coro_in_new_loop)

        # 使用 wrap_future 将 concurrent.futures.Future 包装成 asyncio.Future，
        # 这样它就可以在主事件循环中被 await。
        asyncio_future = asyncio.wrap_future(conc_future, loop=main_loop)

        return await asyncio_future

    def submit(self, coro: Coroutine, on_done: DoneCallback = None, on_fail: FailCallback = None):
        """
        [回调模式] 提交一个协程到线程池中执行，通过回调处理结果。

        :param coro: 需要执行的协程。
        :param on_done: (可选) 任务成功完成时调用的回调函数。
        :param on_fail: (可选) 任务失败时调用的回调函数。
        """
        if not self._is_running:
            if on_fail:
                on_fail(Exception("工作者已停止运行。"))
            return

        def run_coro_in_new_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        def task_done_callback(future):
            try:
                result = future.result()
                if on_done:
                    on_done(result)
            except Exception as e:
                if on_fail:
                    on_fail(e)

        future = self.executor.submit(run_coro_in_new_loop)
        if on_done or on_fail:
            future.add_done_callback(task_done_callback)

    def stop(self):
        """
        优雅地关闭线程池。
        """
        self._is_running = False
        self.executor.shutdown(wait=True)


async_worker = AsyncWorker()
"""
全局单例

可以在项目的其他模块中直接导入此实例来使用
"""
