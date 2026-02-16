import flet as ft
import pyautogui
from .pages.about import main as AboutView
from .pages.changelog import main as ChangelogView
from .pages.history import main as HistoryView
from .pages.home import main as HomeView
from .pages.playlist import main as PlaylistView
from .pages.settings import main as SettingsView


async def main(page: ft.Page):
    page.title = "VSingerBoard"

    width, height = pyautogui.size()
    page.window.width = int(width * 0.9)
    page.window.height = int(height * 0.9)
    page.window.resizable = False

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

    def handle_context_click(e: ft.Event[ft.PopupMenuItem]):
        page.show_dialog(ft.SnackBar(content=f"select '{e.control.content}'"))

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
            leading=ft.IconButton(ft.Icons.MENU, on_click=handle_show_drawer),
            leading_width=40,
            title=ft.Text(title),
            center_title=False,
            bgcolor=ft.Colors.RED_ACCENT,
        )

    def route_change(route):
        page.views.clear()
        match page.route:
            case "/":
                page.views.append(HomeView("home page", create_appbar("点歌列表"), create_drawer(0)))
            case "/history":
                page.views.append(HistoryView("history page", create_appbar("点歌历史"), create_drawer(1)))
            case "/playlist":
                page.views.append(PlaylistView("playlist page", create_appbar("歌单管理"), create_drawer(2)))
            case "/changelog":
                page.views.append(ChangelogView("changelog page", create_appbar("更新日志"), create_drawer(3)))
            case "/settings":
                page.views.append(SettingsView("settings page", create_appbar("设置"), create_drawer(4)))
            case "/about":
                page.views.append(AboutView("about page", create_appbar("关于"), create_drawer(0)))
            case _:
                pass

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change(page.route)
