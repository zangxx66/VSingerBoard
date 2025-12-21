import asyncio
import json
from aiohttp import web
from src.utils import WebSocketServer, logger, async_worker, WebsocketDataItem
from . import douyin_manager, bili_manager


class DoubiWs:
    def __init__(self):
        self._stop_event = asyncio.Event()
        self._run_future = None
        self._ws = None
        self._broadcast_task = None  # 用于周期性广播的任务
        self.bili_room_id = 0
        self.douyin_room_id = 0
        self.bili_status = -1
        self.douyin_status = -1

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
                song_list = douyin_list + bilibili_list
                if len(song_list) > 0 and self._ws:
                    result = {"type": "add", "data": song_list}
                    await self._ws.broadcast(json.dumps(result, ensure_ascii=False))

                douyin_del_list = douyin_manager.get_del_list()
                bilibili_del_list = bili_manager.get_del_list()
                del_list = douyin_del_list + bilibili_del_list
                if len(del_list) > 0 and self._ws:
                    result = {"type": "del", "data": del_list}
                    await self._ws.broadcast(json.dumps(result, ensure_ascii=False))

                bili_room_id = bili_manager.config.room_id
                bili_status = bili_manager.get_status()
                douyin_room_id = douyin_manager.room_id
                douyin_status = douyin_manager.get_status()

                if self.bili_room_id != bili_room_id:
                    self.bili_room_id = bili_room_id
                    await self._ws.broadcast(json.dumps({"type": "bili_room_change", "data": self.bili_room_id}, ensure_ascii=False))
                if self.bili_status != bili_status:
                    self.bili_status = bili_status
                    await self._ws.broadcast(json.dumps({"type": "bili_status_change", "data": self.bili_status}, ensure_ascii=False))
                if self.douyin_room_id != douyin_room_id:
                    self.douyin_room_id = douyin_room_id
                    await self._ws.broadcast(json.dumps({"type": "douyin_room_change", "data": self.douyin_room_id}, ensure_ascii=False))
                if self.douyin_status != douyin_status:
                    self.douyin_status = douyin_status
                    await self._ws.broadcast(json.dumps({"type": "douyin_status_change", "data": self.douyin_status}, ensure_ascii=False))

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
        recive_data = WebsocketDataItem(**json.loads(message))
        if recive_data.type == "clear":
            await self._ws.broadcast(json.dumps({"type": "clear"}, ensure_ascii=False))
        elif recive_data.type == "delete":
            result = {"type": "remove", "data": recive_data.data}
            await self._ws.broadcast(json.dumps(result, ensure_ascii=False))
        elif recive_data.type == "live_config":
            self.bili_room_id = bili_manager.config.room_id
            self.bili_status = bili_manager.get_status()
            self.douyin_room_id = douyin_manager.room_id
            self.douyin_status = douyin_manager.get_status()
            result = {"type": "live_config", "data": {"bilibili_room_id": self.bili_room_id, "bilibili_ws_status": self.bili_status, "douyin_romm_id": self.douyin_room_id, "douyin_ws_status": self.douyin_status}}
            await ws.send_json(result)
        else:
            await ws.send_json({"type": "echo", "data": recive_data.data})

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
