import asyncio
import flet as ft
from src.live import douyin_manager, bili_manager
from src.utils import async_worker, logger


class MessageManager():
    def __init__(self, page: ft.Page):
        self._page = page
        self._stop_event = asyncio.Event()
        self._run_future = None
        self._broadcast_task = None
        self.douyin_status = 0
        self.bilibili_status = 0

    def start(self):
        if self._run_future and not self._run_future.done():
            logger.info("message_manager is already running...")
            return
        self._stop_event.clear()
        self._run_future = async_worker.submit(self._start_and_run_client())
        self._page.pubsub.subscribe_topic("del", self.on_del_message)
        self._page.pubsub.subscribe_topic("clear", self.on_clear_message)
        self._page.pubsub.subscribe_topic("manual", self.on_add_message)
        logger.info("message_manager main task submitted to worker...")

    async def _periodic_broadcast_task(self):
        while not self._stop_event.is_set():
            try:
                douyin_list = douyin_manager.get_list()
                bili_list = bili_manager.get_list()
                combine_list = douyin_list + bili_list
                combine_list.sort(key=lambda x: x["send_time"], reverse=True)
                self._page.pubsub.send_all_on_topic("add", combine_list)

                douyin_status = douyin_manager.get_status()
                if self.douyin_status != douyin_status:
                    dy_connect_status = douyin_status == 1
                    dy_msg = "抖音已连接" if dy_connect_status else "抖音未连接"
                    self.douyin_status = douyin_status
                    self._page.pubsub.send_all_on_topic("notify", {"is_connect": dy_connect_status, "message": dy_msg})
                bilibili_status = bili_manager.get_status()
                if self.bilibili_status != bilibili_status:
                    bili_connect_status = bilibili_status == 2
                    bili_msg = "哔哩哔哩已连接" if bili_connect_status else "哔哩哔哩未连接"
                    self.bilibili_status = bilibili_status
                    self._page.pubsub.send_all_on_topic("notify", {"is_connect": bili_connect_status, "message": bili_msg})

                await asyncio.sleep(2)
            except asyncio.CancelledError:
                logger.info("periodic broadcast task was cancelled...")
                break
            except Exception as ex:
                logger.error(f"Error in periodic broadcast task: {ex}")
                await asyncio.sleep(2)

    async def _start_and_run_client(self):
        self._broadcast_task = None
        try:
            self._broadcast_task = asyncio.create_task(self._periodic_broadcast_task())
            await self._stop_event.wait()
        except asyncio.CancelledError:
            logger.warning("message_manager task was cancelled...")
        except Exception as ex:
            logger.error(f"message_manager task failed: {ex}")
        finally:
            if self._broadcast_task:
                self._broadcast_task.cancel()
                await asyncio.gather(self._broadcast_task, return_exceptions=True)
            logger.info("message_manager resources cleaned up...")

    async def on_del_message(self, _, del_dict: dict):
        source = del_dict["source"]
        if source == "bilibili":
            bili_manager.del_list(del_dict["msg_id"])
        if source == "douyin":
            douyin_manager.del_list(del_dict["msg_id"])

    def on_clear_message(self, _):
        bili_manager.clear_list()
        douyin_manager.clear_list()

    def on_add_message(self, _, data: dict):
        source = data["source"]
        if source == "bilibili":
            bili_manager.add_list(data["data"])
        if source == "douyin":
            douyin_manager.add_list(data["data"])

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
