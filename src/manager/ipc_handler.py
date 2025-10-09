import asyncio
from src.utils import IPCManager, MessageQueueEmpty, logger, async_worker
from src.live import bili_manager, douyin_manager

ipc_manager = IPCManager()
is_done = False
ipc_task_thread = None


async def ipc_task():
    global is_done
    while not is_done:
        try:
            received_data = ipc_manager.receive_message_nonblocking()
            if received_data == "bilibili_ws_reconnect":
                logger.info("bilibili_ws_reconnect")
                await bili_manager.stop()
                await asyncio.sleep(1)
                bili_manager.start()
            elif received_data == "douyin_ws_reconnect":
                logger.info("douyin_ws_reconnect")
                await douyin_manager.stop()
                await asyncio.sleep(1)
                douyin_manager.start()
            else:
                logger.info(f"Received data: {received_data}")
        except MessageQueueEmpty:
            pass
        await asyncio.sleep(0.1)

    logger.info("IPC task stopped.")


def start_ipc_task():
    global ipc_task_thread
    ipc_task_thread = async_worker.submit(ipc_task())


def stop_ipc_task():
    global is_done
    is_done = True
    if ipc_task_thread and not ipc_task_thread.done():
        ipc_task_thread.cancel()
        logger.info("IPC task thread joined.")
