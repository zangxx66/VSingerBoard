import asyncio
from src.utils import logger, async_worker, is_internet_available, send_notification
from src.live import bili_manager, douyin_manager

network_check = True
network_process = None
network_count = 0


def start_websocket_server():
    global doubi_thread
    logger.info("------start websocket------")
    bili_manager.start()
    douyin_manager.start()


def start_network_check():
    global network_process
    network_process = async_worker.submit(network_available_check())


async def network_available_check():
    global network_count
    while network_check:
        if not is_internet_available(port=443):
            if network_count == 0:
                send_notification("警告", "网络已断开连接")
            network_count = 1
        else:
            network_count = 0
        await asyncio.sleep(5)


def stop_all_servers():
    global network_check, network_process
    from concurrent.futures import wait

    network_check = False
    if network_process:
        network_process.cancel()

    bili_future = async_worker.submit(bili_manager.stop())
    douyin_future = async_worker.submit(douyin_manager.stop())
    wait([bili_future, douyin_future])
