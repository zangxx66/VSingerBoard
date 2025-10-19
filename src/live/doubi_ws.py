import asyncio
import json
from aiohttp import web
from src.utils import WebSocketServer, logger, async_worker
from . import douyin_manager, bili_manager


class DoubiWs:
    def __init__(self):
        self._stop_event = asyncio.Event()
        self._run_future = None
        self._ws = None
        self._broadcast_task = None  # 用于周期性广播的任务

    def start(self):
        """
        以非阻塞方式提交主任务到工作线程。
        """
        if self._run_future and not self._run_future.done():
            logger.info("DoubiWs is already running.")
            return
        self._stop_event.clear()
        self._run_future = async_worker.submit(self._start_and_run_client())
        logger.info("DoubiWs main task submitted to worker.")

    async def _periodic_broadcast_task(self, interval_seconds: int = 2):
        """
        周期性获取弹幕列表并广播。
        这是一个后台任务。
        """
        while not self._stop_event.is_set():
            try:
                douyin_list = douyin_manager.get_list()
                bilibili_list = bili_manager.get_list()
                result = douyin_list + bilibili_list
                if len(result) > 0 and self._ws:
                    await self._ws.broadcast(json.dumps(result, ensure_ascii=False))

                # 等待一段时间, 避免CPU占用过高, 并让出控制权
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                logger.info("Periodic broadcast task was cancelled.")
                break
            except Exception as e:
                logger.error(f"Error in periodic broadcast task: {e}")
                # 发生错误后也等待, 避免快速失败循环
                await asyncio.sleep(interval_seconds)

    async def _start_and_run_client(self):
        """
        启动WebSocket服务器并管理广播任务的生命周期。
        """
        self._ws = None
        self._broadcast_task = None
        try:
            self._ws = WebSocketServer(host="127.0.0.1")
            await self._ws.start()
            self._ws.on_message = self._on_message
            logger.info("DoubiWs WebSocket server started.")

            # 将周期性广播作为后台任务启动
            self._broadcast_task = asyncio.create_task(self._periodic_broadcast_task())

            # 等待停止信号
            await self._stop_event.wait()
        except asyncio.CancelledError:
            logger.warning("DoubiWs main task was cancelled.")
        except Exception as e:
            logger.error(f"DoubiWs main task failed: {e}")
        finally:
            # 清理广播任务
            if self._broadcast_task:
                self._broadcast_task.cancel()
                # 等待任务确实被取消
                await asyncio.gather(self._broadcast_task, return_exceptions=True)
            # 清理WebSocket服务器
            if self._ws:
                await self._ws.stop()
                self._ws = None
            logger.info("DoubiWs resources cleaned up.")

    async def _on_message(self, ws: web.WebSocketResponse, message: str):
        if message == "clear danmaku":
            await self._ws.broadcast("clear danmaku")
        elif message.startswith("delete"):
            await self._ws.broadcast(message)
        else:
            await ws.send_str(f"Echo: {message}")

    async def stop(self):
        """
        停止主任务和所有相关服务。
        """
        if self._run_future and not self._run_future.done():
            logger.info("Stopping DoubiWs main task.")
            self._stop_event.set()
            try:
                # 等待在工作线程中运行的 future 完成
                awaitable_future = asyncio.wrap_future(self._run_future)
                await asyncio.wait_for(awaitable_future, timeout=5)
            except asyncio.TimeoutError:
                logger.warning("Timed out waiting for DoubiWs task to stop, cancelling.")
                self._run_future.cancel()
            except Exception as e:
                logger.error(f"Error waiting for DoubiWs task to stop: {e}")
            logger.info("DoubiWs main task stopped.")
        self._run_future = None


doubi_manager = DoubiWs()
