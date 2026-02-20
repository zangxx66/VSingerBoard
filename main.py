import os
import flet as ft
from src.utils import logger, async_worker
from src.ui.layout import main
from src.manager import server_manager, subscribe_manager


def run_app():
    logger.info("------ Application Startup ------")

    try:
        async_worker.start()
        async_worker.submit(subscribe_manager.start_subscribe())

        server_manager.start_websocket_server()
        server_manager.start_network_check()

        ft.run(main, name="点歌姬", view=ft.AppView.FLET_APP_WEB)
    except Exception as ex:
        logger.exception(ex)
    finally:
        subscribe_manager.stop_subscribe()
        server_manager.stop_all_servers()
        async_worker.stop()
        logger.info("------ Application Stop ------")
        os._exit(0)


if __name__ == "__main__":
    run_app()
