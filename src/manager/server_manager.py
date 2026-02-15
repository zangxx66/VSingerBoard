import subprocess
import threading
import asyncio
from src.utils import logger, async_worker, is_internet_available, send_notification
from src.server import startup
from src.live import bili_manager, douyin_manager, doubi_manager

server_process = None
dev_process = None
vite_thread = None
network_check = True
network_process = None
network_count = 0


def vite_server():
    global dev_process
    dev_process = subprocess.Popen("pnpm run -C frontend/ dev", shell=True)
    dev_process.communicate()


def start_http_server():
    global server_process
    logger.info("------start HTTP server------")
    server_process = threading.Thread(target=startup, name="FastApi", daemon=True)
    server_process.start()


def start_vite_server():
    global vite_thread
    logger.info("------startup Vite server------")

    vite_thread = threading.Thread(target=vite_server, name="Vite Thread", daemon=True)
    vite_thread.start()


def start_websocket_server():
    global doubi_thread
    logger.info("------start websocket------")
    bili_manager.start()
    douyin_manager.start()
    doubi_manager.start()


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
    global dev_process, vite_thread, server_process, network_check, network_process
    from concurrent.futures import wait

    network_check = False
    if network_process:
        network_process.cancel()

    bili_future = async_worker.submit(bili_manager.stop())
    douyin_future = async_worker.submit(douyin_manager.stop())
    doubi_future = async_worker.submit(doubi_manager.stop())
    wait([bili_future, douyin_future, doubi_future])

    if dev_process:
        dev_process.terminate()
        logger.info("Vite server stopped.")
        dev_process = None
    if vite_thread:
        vite_thread.join(timeout=5)
        logger.info("Vite thread stopped.")
        vite_thread = None
    if server_process:
        server_process.join(timeout=5)
        logger.info("FastApi server stopped.")
        server_process = None
