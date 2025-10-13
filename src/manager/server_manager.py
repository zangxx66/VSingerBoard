import multiprocessing
import subprocess
import threading
from src.utils import IPCManager, logger, async_worker
from src.server import startup
from src.live import bili_manager, douyin_manager, doubi_manager

server_process = None
dev_process = None
vite_thread = None


def vite_server():
    global dev_process
    dev_process = subprocess.Popen("npm run -C frontend/ dev", shell=True)
    dev_process.communicate()


def start_http_server(token: str, ipc_manager: IPCManager):
    global server_process
    logger.info("------start HTTP server------")
    server_process = multiprocessing.Process(target=startup, args=(token, ipc_manager), name="FastApi")
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


def stop_all_servers():
    global dev_process, vite_thread, server_process
    async_worker.submit(bili_manager.stop())
    async_worker.submit(douyin_manager.stop())
    async_worker.submit(doubi_manager.stop())

    if dev_process:
        dev_process.terminate()
        logger.info("Vite server stopped.")
        dev_process = None
    if vite_thread:
        vite_thread.join(timeout=5)
        logger.info("Vite thread stopped.")
        vite_thread = None
    if server_process:
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            logger.warning("Server process did not terminate in time, forcing kill.")
            server_process.kill()
            server_process.join()
        server_process.close()
        logger.info("FastApi server stopped.")
        server_process = None
