import asyncio
from . import subscribe_manager, cancel_subscribe
from src.live import douyin_manager, bili_manager
from src.utils import async_worker, logger, DanmuInfo, EventEmitter


class MessageManager():
    def __init__(self, event_emitter: EventEmitter):
        self.events = event_emitter
        self._stop_event = asyncio.Event()
        self._run_future = None
        self.douyin_status = 0
        self.bilibili_status = 0
        self.danmaku_list: list[DanmuInfo] = []

    def start(self):
        if self._run_future and not self._run_future.done():
            logger.info("message_manager is already running...")
            return
        self._stop_event.clear()
        self._run_future = async_worker.submit(self._start_and_run_client())
        logger.info("message_manager main task submitted to worker...")

    async def _periodic_broadcast_task(self):
        if not self._stop_event.is_set():
            try:
                douyin_list = douyin_manager.get_list()
                bili_list = bili_manager.get_list()
                combine_list = douyin_list + bili_list
                if set(combine_list) != set(self.danmaku_list):
                    combine_list.sort(key=lambda x: x.send_time, reverse=True)
                    self.danmaku_list = combine_list[:]
                    await self.events.emit("on_message_update", self.danmaku_list)

                douyin_status = douyin_manager.get_status()
                if self.douyin_status != douyin_status:
                    dy_connect_status = douyin_status == 1
                    dy_msg = "抖音已连接" if dy_connect_status else "抖音未连接"
                    self.douyin_status = douyin_status
                    await self.events.emit("on_status_change", {"is_connect": dy_connect_status, "message": dy_msg})
                
                bilibili_status = bili_manager.get_status()
                if self.bilibili_status != bilibili_status:
                    bili_connect_status = bilibili_status == 2
                    bili_msg = "哔哩哔哩已连接" if bili_connect_status else "哔哩哔哩未连接"
                    self.bilibili_status = bilibili_status
                    await self.events.emit("on_status_change", {"is_connect": bili_connect_status, "message": bili_msg})

            except asyncio.CancelledError:
                logger.info("periodic broadcast task was cancelled...")
            except Exception as ex:
                logger.error(f"Error in periodic broadcast task: {ex}")

    async def _start_and_run_client(self):
        try:
            subscribe_manager.register("interval", seconds=2, id="flet_on_notify", replace_existing=True)(self._periodic_broadcast_task)
            await self._stop_event.wait()
        except asyncio.CancelledError:
            logger.warning("message_manager task was cancelled...")
        except Exception as ex:
            logger.error(f"message_manager task failed: {ex}")
        finally:
            cancel_subscribe("flet_on_notify")
            logger.info("message_manager resources cleaned up...")

    def delete_message(self, source: str, msg_id: int):
        """
        删除单条消息
        """
        if source == "bilibili":
            bili_manager.del_list(msg_id)
        if source == "douyin":
            douyin_manager.del_list(msg_id)

    async def clear_all_messages(self):
        """
        清空所有消息
        """
        bili_manager.clear_list()
        douyin_manager.clear_list()
        await self.events.emit("on_message_update", [])

    def add_manual_message(self, data: dict):
        """
        手动添加消息
        """
        source = data["source"]
        if source == "bilibili":
            bili_manager.add_list(data["data"])
        if source == "douyin":
            douyin_manager.add_list(data["data"])

    async def sync_current_messages(self):
        """
        手动触发同步当前列表（对应原 on_mount）
        """
        await self.events.emit("on_message_update", self.danmaku_list)

    async def stop(self):
        if self._run_future and not self._run_future.done():
            self._stop_event.set()
            try:
                awaitable_future = asyncio.wrap_future(self._run_future)
                await asyncio.wait_for(awaitable_future, timeout=5)
            except asyncio.TimeoutError:
                logger.warning("Timed out waiting for message_manager task to stop, cancelling...")
                self._run_future.cancel()
            except Exception as ex:
                logger.error(f"Error waiting for message_manager task to stop: {ex}")
            logger.info("message_manager main task stopped...")
        self._run_future = None
