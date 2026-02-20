import flet as ft
import pyautogui
import asyncio
from .pages.about import main as AboutView
from .pages.changelog import main as ChangelogView
from .pages.history import main as HistoryView
from .pages.home import main as HomeView
from .pages.playlist import main as PlaylistView
from .pages.settings import main as SettingsView
from src.utils import resource_path, DanmuInfo, logger, async_worker
from src.live import douyin_manager, bili_manager


class message_manager():
    def __init__(self, page: ft.Page):
        self._page = page
        self._stop_event = asyncio.Event()
        self._run_future = None
        self._broadcast_task = None
        self.song_list: list[DanmuInfo] = []

    def start(self):
        if self._run_future and not self._run_future.done():
            logger.info("message_manager is already running...")
            return
        self._stop_event.clear()
        self._run_future = async_worker.submit(self._start_and_run_client())
        logger.info("message_manager main task submitted to worker...")

    async def _periodic_broadcast_task(self):
        while not self._stop_event.is_set():
            try:
                douyin_list = douyin_manager.get_list()
                bili_list = bili_manager.get_list()
                song_list = douyin_list + bili_list
                self._page.pubsub.send_all(song_list)

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


async def main(page: ft.Page):
    page.title = "点歌姬"

    width, height = pyautogui.size()
    page.window.width = int(width * .9)
    page.window.height = int(height * .9)
    page.locale_configuration = ft.LocaleConfiguration([ft.Locale("zh", "Hans")], ft.Locale("zh", "Hans"))
    page.window.resizable = False
    page.window.shadow = True
    page.window.icon = resource_path("icons/logo.ico")
    page.window.title_bar_buttons_hidden = True
    page.window.title_bar_hidden = True
    page.window.alignment = ft.Alignment.CENTER

    message_handler = message_manager(page)
    message_handler.start()

    def handle_minimized_window(e: ft.Event[ft.IconButton]):
        page.window.minimized = True

    async def handle_close_window(e: ft.Event[ft.IconButton]):
        await page.window.close()

    async def handle_show_drawer():
        await page.show_drawer()

    async def handle_drawer_change(e: ft.Event[ft.NavigationDrawer]):
        match e.control.selected_index:
            case 0:
                await page.push_route("/")
            case 1:
                await page.push_route("/history")
            case 2:
                await page.push_route("/playlist")
            case 3:
                await page.push_route("/changelog")
            case 4:
                await page.push_route("/settings")
            case 5:
                await page.push_route("/about")
            case _:
                await page.push_route("/")

    def create_drawer(select_index=0):
        return ft.NavigationDrawer(
            selected_index=select_index,
            on_change=handle_drawer_change,
            controls=[
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    label="点歌板",
                    icon=ft.Icons.HOME,
                    selected_icon=ft.Icon(ft.Icons.HOME),
                ),
                ft.NavigationDrawerDestination(
                    label="点歌历史",
                    icon=ft.Icons.CALENDAR_TODAY,
                    selected_icon=ft.Icon(ft.Icons.CALENDAR_TODAY),
                ),
                ft.NavigationDrawerDestination(
                    label="歌单管理",
                    icon=ft.Icons.COLLECTIONS,
                    selected_icon=ft.Icon(ft.Icons.COLLECTIONS),
                ),
                ft.NavigationDrawerDestination(
                    label="更新日志",
                    icon=ft.Icons.HISTORY,
                    selected_icon=ft.Icon(ft.Icons.HISTORY),
                ),
                ft.NavigationDrawerDestination(
                    label="设置",
                    icon=ft.Icons.SETTINGS,
                    selected_icon=ft.Icon(ft.Icons.SETTINGS),
                ),
                ft.NavigationDrawerDestination(
                    label="关于",
                    icon=ft.Icons.INFO,
                    selected_icon=ft.Icon(ft.Icons.INFO),
                ),
            ]
        )

    def create_appbar(title):
        return ft.AppBar(
            leading=ft.IconButton(ft.Icons.MENU, padding=ft.Padding(left=24), hover_color=ft.Colors.TRANSPARENT, on_click=handle_show_drawer),
            leading_width=40,
            title=ft.Text(title),
            center_title=False,
            bgcolor=ft.Colors.RED_ACCENT,
            actions_padding=ft.Padding(right=24),
            actions=[
                ft.IconButton(ft.Icons.MINIMIZE, on_click=handle_minimized_window),
                ft.IconButton(ft.Icons.CLOSE, on_click=handle_close_window)
            ]
        )

    def route_change(route):
        page.views.clear()
        match page.route:
            case "/":
                page.views.append(HomeView(page, create_appbar("点歌列表"), create_drawer(0)))
            case "/history":
                page.views.append(HistoryView(page, create_appbar("点歌历史"), create_drawer(1)))
            case "/playlist":
                page.views.append(PlaylistView(page, create_appbar("歌单管理"), create_drawer(2)))
            case "/changelog":
                page.views.append(ChangelogView(page, create_appbar("更新日志"), create_drawer(3)))
            case "/settings":
                page.views.append(SettingsView(page, create_appbar("设置"), create_drawer(4)))
            case "/about":
                page.views.append(AboutView(page, create_appbar("关于"), create_drawer(5)))
            case _:
                pass

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change(page.route)
