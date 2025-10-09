import multiprocessing
import subprocess
from src.utils import IPCManager, logger
from src.server import startup
from src.jsBridge import start_bili, start_dy, stop_bili, stop_dy

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
    start_bili()
    start_dy()


def stop_all_servers():
    stop_bili()
    stop_dy()
    if dev_process is not None:
        dev_process.terminate()
    if server_process is not None:
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            logger.warning("Server process did not terminate in time, forcing kill.")
            server_process.kill()
            server_process.join()
        server_process.close()
