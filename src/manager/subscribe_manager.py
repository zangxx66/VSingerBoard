from src.database import Db
from src.utils import logger, send_notification, check_for_updates
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SubscribeManager:
    def __init__(self):
        self._scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

    def register(self, trigger, **trigger_args):
        def decorator(func):
            logger.info(
                f"Registering background task '{func.__name__}' with trigger '{trigger}' and args {trigger_args}"
            )
            self._scheduler.add_job(func, trigger=trigger, **trigger_args)
            return func

        return decorator

    def start(self):
        if self._scheduler.running:
            logger.warning("Scheduler is already running.")
            return
        logger.info("Starting scheduler...")
        self._scheduler.start()

    def stop(self, wait=True):
        if not self._scheduler.running:
            logger.info("Scheduler is not running.")
            return
        logger.info("Shutting down scheduler...")
        self._scheduler.shutdown(wait=wait)


subscribe_manager = SubscribeManager()
add_job = subscribe_manager.register


async def start_subscribe():
    logger.info("start_subscribe called")
    subscribe_manager.start()
    config = await Db.get_gloal_config()
    if config and config.check_update:
        add_job("interval", hours=5, id="check_updates", replace_existing=True)(check_update)


def stop_subscribe():
    logger.info("stop subscribe")
    subscribe_manager.stop()


def cancel_subscribe(id):
    try:
        subscribe_manager._scheduler.remove_job(id)
        logger.info(f"remove job {id}")
    except Exception:
        logger.warning(f"job {id} was not found")


async def check_update():
    result = await check_for_updates()
    if result["code"] == -1:
        send_notification("提示", result["msg"])
        return
    if result["code"] == 0 and result["url"]:
        send_notification("提示", result["msg"])
