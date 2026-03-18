import flet as ft
from .components import ModernToast
from .pages.about import main as AboutView
from .pages.changelog import main as ChangelogView
from .pages.history import main as HistoryView
from .pages.home import main as HomeView
from .pages.playlist import main as PlaylistView
from .pages.settings import main as SettingsView
from src.utils import resource_path
from src.manager.messages import MessageManager


async def main(page: ft.Page):
    page.title = "点歌姬"

    page.window.width = int(1920 * .8)
    page.window.height = int(1080 * .8)
    page.window.full_screen = False
    page.window.resizable = False
    page.window.shadow = True
    page.window.icon = resource_path("icons/logo.ico")
    page.window.title_bar_buttons_hidden = True
    page.window.title_bar_hidden = True
    page.window.alignment = ft.Alignment.CENTER
    page.locale_configuration = ft.LocaleConfiguration([ft.Locale("zh", "Hans")], ft.Locale("zh", "Hans"))
    page.fonts = {"AlibabaPuHuiTi": resource_path("fonts/AlibabaPuHuiTi-Medium.ttf")}
    page.theme = ft.Theme(
        appbar_theme=ft.AppBarTheme(bgcolor=ft.Colors.PINK_ACCENT_200, shadow_color=ft.Colors.GREY_800),
        color_scheme=ft.ColorScheme(primary=ft.Colors.PINK),
        color_scheme_seed=ft.Colors.PINK,
        dialog_theme=ft.DialogTheme(shadow_color=ft.Colors.ON_SURFACE_VARIANT),
        font_family="AlibabaPuHuiTi",
    )

    message_handler = MessageManager(page)
    message_handler.start()

    def on_notify(_, msg: dict[str, bool]):
        if msg["is_connect"]:
            ModernToast.success(
                page,
                msg["message"]
            )
        else:
            ModernToast.warning(
                page,
                msg["message"]
            )

    page.pubsub.subscribe_topic("notify", on_notify)

    def handle_minimized_window(e: ft.Event[ft.IconButton]):
        page.window.minimized = True

    async def handle_exit(e: ft.Event[ft.TextButton]):
        await message_handler.stop()
        await page.window.close()

    async def handle_close_window(e: ft.Event[ft.IconButton]):
        page.show_dialog(ft.AlertDialog(
            title=ft.Text("提示"),
            content=ft.Text("是否退出？"),
            actions=[
                ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                ft.TextButton("退出", on_click=handle_exit)
            ]
        ))

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

    drawer = ft.NavigationDrawer(
        selected_index=0,
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

    app_bar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.MENU, padding=ft.Padding.only(left=10), hover_color=ft.Colors.TRANSPARENT, on_click=handle_show_drawer),
        leading_width=40,
        center_title=False,
        actions_padding=ft.Padding.only(right=24),
        actions=[
            ft.IconButton(ft.Icons.MINIMIZE, tooltip="最小化", on_click=handle_minimized_window),
            ft.IconButton(ft.Icons.CLOSE, tooltip="退出", on_click=handle_close_window)
        ]
    )

    def route_change(route):
        page.views.clear()
        match page.route:
            case "/":
                app_bar.title = ft.Text("点歌列表")
                drawer.selected_index = 0
                page.views.append(HomeView(page))
            case "/history":
                app_bar.title = ft.Text("点歌历史")
                drawer.selected_index = 1
                page.views.append(HistoryView(page))
            case "/playlist":
                app_bar.title = ft.Text("歌单管理")
                drawer.selected_index = 2
                page.views.append(PlaylistView(page))
            case "/changelog":
                app_bar.title = ft.Text("更新日志")
                drawer.selected_index = 3
                page.views.append(ChangelogView(page))
            case "/settings":
                app_bar.title = ft.Text("设置")
                drawer.selected_index = 4
                page.views.append(SettingsView(page))
            case "/about":
                app_bar.title = ft.Text("关于")
                drawer.selected_index = 5
                page.views.append(AboutView(page))
            case _:
                pass
        page.appbar = app_bar
        page.drawer = drawer

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change(page.route)
