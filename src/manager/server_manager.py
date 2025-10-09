import multiprocessing
import subprocess
from src.utils import IPCManager, logger, async_worker
from src.server import startup
from src.live import bili_manager, douyin_manager

server_process = None
dev_process = None


def start_http_server(token: str, ipc_manager: IPCManager):
    global server_process
    logger.info("------start HTTP server------")
    server_process = multiprocessing.Process(target=startup, args=(token, ipc_manager), name="FastApi")
    server_process.start()


def start_vite_server():
    global dev_process
    logger.info("------startup Vite server------")
    dev_process = subprocess.Popen("npm run -C frontend/ dev", shell=True)
    dev_process.communicate()


def start_websocket_server():
    logger.info("------start websocket------")
    bili_manager.start()
    douyin_manager.start()


def stop_all_servers():
    async_worker.run_sync(bili_manager.stop())
    async_worker.run_sync(douyin_manager.stop())

    if dev_process:
        dev_process.terminate()
        logger.info("Vite server stopped.")
    if server_process and server_process.exitcode:
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            logger.warning("Server process did not terminate in time, forcing kill.")
            server_process.kill()
            server_process.join()
        server_process.close()
        logger.info("FastApi server stopped.")
