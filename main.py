from src.utils import logger
from src.ui.layout import main
import flet as ft


def run_app():
    logger.info("------ Application Startup ------")

    try:
        ft.run(main, view=ft.AppView.FLET_APP_WEB)
    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    run_app()
