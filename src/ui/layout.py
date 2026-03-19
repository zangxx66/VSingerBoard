import flet as ft
from flet import AppBar, NavigationDrawer, Ref
from .components import ModernToast
from .pages.about import main as AboutView
from .pages.changelog import main as ChangelogView
from .pages.history import main as HistoryView
from .pages.home import main as HomeView
from .pages.playlist import main as PlaylistView
from .pages.settings import main as SettingsView
from src.utils import resource_path, EventEmitter, globalfigItem
from src.manager import MessageManager
from src.database import Db as db


async def main(page: ft.Page):
    page.title = "点歌姬"

    # flet 属性初始设置
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
        button_theme=ft.ButtonTheme(style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30))),
        color_scheme=ft.ColorScheme(primary=ft.Colors.PINK),
        color_scheme_seed=ft.Colors.PINK,
        dialog_theme=ft.DialogTheme(shadow_color=ft.Colors.ON_SURFACE_VARIANT),
        font_family="AlibabaPuHuiTi",
    )

    # AppBar，抽屉导航，系统主题设置
    app_bar: AppBar | None = None
    drawer: NavigationDrawer | None = None
    global_config: globalfigItem | None = None
    theme_destination = Ref[ft.NavigationDrawerDestination]()

    # 事件分发器
    event_bus = EventEmitter()
    message_handler = MessageManager(event_bus)
    page.data = {"message_handler": message_handler}
    message_handler.start()

    def on_notify(msg: dict[str, bool]):
        """
        toast 通知
        """
        def show_toast():
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
        page.run_thread(show_toast)

    event_bus.on("on_status_change", on_notify)

    def handle_keyboard(e: ft.KeyboardEvent):
        if e.key == "Escape":
            return

    def handle_minimized_window(e: ft.Event[ft.IconButton]):
        """
        最小化
        """
        page.window.minimized = True

    async def handle_exit(e: ft.Event[ft.TextButton]):
        """
        退出应用
        """
        await message_handler.stop()
        await page.window.close()

    async def handle_close_window(e: ft.Event[ft.IconButton]):
        """
        退出确认
        """
        page.show_dialog(ft.AlertDialog(
            title=ft.Text("提示"),
            content=ft.Text("是否退出？"),
            actions=[
                ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                ft.TextButton("退出", on_click=handle_exit)
            ]
        ))

    async def handle_theme_switch():
        """
        切换主题
        """
        result = await db.add_or_update_gloal_config(**{"id": global_config.id, "dark_mode": not global_config.dark_mode})
        if result == 0:
            ModernToast.warning(page, "切换失败")
        else:
            global_config.dark_mode = not global_config.dark_mode
            page.theme_mode = ft.ThemeMode.DARK if global_config.dark_mode else ft.ThemeMode.LIGHT
            theme_destination.current.label = "DARK" if global_config.dark_mode else "LIGHT"
            theme_destination.current.icon = ft.Icons.DARK_MODE if global_config.dark_mode else ft.Icons.LIGHT_MODE
            theme_destination.current.selected_icon = ft.Icons.DARK_MODE if global_config.dark_mode else ft.Icons.LIGHT_MODE
            ModernToast.success(page, "切换成功")

    async def on_mount():
        """
        初始化主题
        """
        nonlocal global_config
        global_config = await db.get_gloal_config()
        if global_config:
            page.theme_mode = ft.ThemeMode.DARK if global_config.dark_mode else ft.ThemeMode.LIGHT
        else:
            global_config = globalfigItem()
            global_config.id = 0
            global_config.dark_mode = False
            page.theme_mode = ft.ThemeMode.LIGHT
        theme_destination.current.label = "DARK" if global_config.dark_mode else "LIGHT"
        theme_destination.current.icon = ft.Icons.DARK_MODE if global_config.dark_mode else ft.Icons.LIGHT_MODE
        theme_destination.current.selected_icon = ft.Icons.DARK_MODE if global_config.dark_mode else ft.Icons.LIGHT_MODE

    async def handle_show_drawer():
        """
        打开抽屉导航
        """
        await page.show_drawer()

    async def handle_drawer_change(e: ft.Event[ft.NavigationDrawer]):
        """
        抽屉导航点击事件
        """
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
            case 6:
                await handle_theme_switch()
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
            ft.NavigationDrawerDestination(
                label="LIGHT",
                icon=ft.Icons.LIGHT_MODE,
                selected_icon=ft.Icons.LIGHT_MODE,
                ref=theme_destination,
            )
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
    page.on_keyboard_event = handle_keyboard

    page.run_task(on_mount)

    route_change(page.route)
