import flet as ft
from flet import NavigationDrawer, Ref
from .controls import ModernToast, MenuBar
from .pages.about import main as AboutView
from .pages.changelog import main as ChangelogView
from .pages.history import main as HistoryView
from .pages.home import main as HomeView
from .pages.playlist import main as PlaylistView
from .pages.settings import main as SettingsView
from .pages.statistic import main as StatisticView
from src.utils import resource_path, EventEmitter, globalfigItem
from src.manager import MessageManager
from src.database import Db as db


async def main(page: ft.Page):
    page.title = "点歌姬"

    # flet 属性初始设置
    page.window.width = int(1920 * 0.8)
    page.window.height = int(1080 * 0.8)
    page.window.full_screen = False
    page.window.resizable = False
    page.window.shadow = True
    page.window.icon = resource_path("icons/logo.ico")
    page.window.title_bar_buttons_hidden = True
    page.window.title_bar_hidden = True
    page.window.alignment = ft.Alignment.CENTER
    page.locale_configuration = ft.LocaleConfiguration(
        [ft.Locale("zh", "Hans")], ft.Locale("zh", "Hans")
    )
    page.fonts = {"AlibabaPuHuiTi": resource_path("fonts/AlibabaPuHuiTi-Medium.ttf")}
    page.theme = ft.Theme(
        appbar_theme=ft.AppBarTheme(
            bgcolor=ft.Colors.PINK_ACCENT_200, shadow_color=ft.Colors.GREY_800
        ),
        button_theme=ft.ButtonTheme(
            style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30))
        ),
        color_scheme=ft.ColorScheme(primary=ft.Colors.PINK),
        color_scheme_seed=ft.Colors.PINK,
        dialog_theme=ft.DialogTheme(shadow_color=ft.Colors.ON_SURFACE_VARIANT),
        font_family="AlibabaPuHuiTi",
        page_transitions=ft.PageTransitionsTheme(
            macos=ft.PageTransitionTheme.FADE_UPWARDS,
            windows=ft.PageTransitionTheme.FADE_UPWARDS,
            linux=ft.PageTransitionTheme.FADE_UPWARDS
        )
    )

    # 抽屉导航，系统主题设置
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
                ModernToast.success(page, msg["message"])
            else:
                ModernToast.warning(page, msg["message"])

        page.run_thread(show_toast)

    event_bus.on("on_status_change", on_notify)

    def handle_keyboard(e: ft.KeyboardEvent):
        if e.key == "Escape":
            return

    def handle_minimized_window(_: ft.Event[ft.IconButton]):
        """
        最小化
        """
        page.window.minimized = True

    async def handle_exit(_: ft.Event[ft.TextButton]):
        """
        退出应用
        """
        await message_handler.stop()
        await page.window.close()

    async def handle_close_window(_: ft.Event[ft.IconButton]):
        """
        退出确认
        """
        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text("是否退出？"),
                actions=[
                    ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                    ft.TextButton("退出", on_click=handle_exit),
                ],
            )
        )

    async def handle_theme_switch():
        """
        切换主题
        """
        result = await db.add_or_update_gloal_config(
            **{"id": global_config.id, "dark_mode": not global_config.dark_mode}
        )
        if result == 0:
            ModernToast.warning(page, "切换失败")
        else:
            global_config.dark_mode = not global_config.dark_mode
            theme_icon = ft.Icons.DARK_MODE if global_config.dark_mode else ft.Icons.LIGHT_MODE
            page.theme_mode = (
                ft.ThemeMode.DARK if global_config.dark_mode else ft.ThemeMode.LIGHT
            )
            theme_destination.current.label = (
                "DARK" if global_config.dark_mode else "LIGHT"
            )
            theme_destination.current.icon = theme_icon
            theme_destination.current.selected_icon = theme_icon
            ModernToast.success(page, "切换成功")

    async def on_mount():
        """
        初始化主题
        """
        nonlocal global_config
        global_config = await db.get_gloal_config()
        if global_config:
            page.theme_mode = (
                ft.ThemeMode.DARK if global_config.dark_mode else ft.ThemeMode.LIGHT
            )
        else:
            global_config = globalfigItem()
            global_config.id = 0
            global_config.dark_mode = False
            page.theme_mode = ft.ThemeMode.LIGHT
        theme_icon = ft.Icons.DARK_MODE if global_config.dark_mode else ft.Icons.LIGHT_MODE
        theme_destination.current.label = "DARK" if global_config.dark_mode else "LIGHT"
        theme_destination.current.icon = theme_icon
        theme_destination.current.selected_icon = theme_icon

    async def handle_show_drawer(_: ft.Event[ft.IconButton]):
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
                await page.push_route("/statistic")
            case 4:
                await page.push_route("/settings")
            case 5:
                await page.push_route("/changelog")
            case 6:
                await page.push_route("/about")
            case 7:
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
                label="统计",
                icon=ft.Icons.DONUT_LARGE,
                selected_icon=ft.Icons.DONUT_LARGE
            ),
            ft.NavigationDrawerDestination(
                label="设置",
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icon(ft.Icons.SETTINGS),
            ),
            ft.NavigationDrawerDestination(
                label="更新日志",
                icon=ft.Icons.HISTORY,
                selected_icon=ft.Icon(ft.Icons.HISTORY),
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
            ),
        ],
    )

    def route_change(route):
        page.views.clear()
        title = ft.Text(size=20)
        match page.route:
            case "/":
                title.value = "点歌列表"
                drawer.selected_index = 0
                page.views.append(HomeView(page))
            case "/history":
                title.value = "点歌历史"
                drawer.selected_index = 1
                page.views.append(HistoryView(page))
            case "/playlist":
                title.value = "歌单管理"
                drawer.selected_index = 2
                page.views.append(PlaylistView(page))
            case "/statistic":
                title.value = "统计"
                drawer.selected_index = 3
                page.views.append(StatisticView(page))
            case "/settings":
                title.value = "设置"
                drawer.selected_index = 4
                page.views.append(SettingsView(page))
            case "/changelog":
                title.value = "更新日志"
                drawer.selected_index = 5
                page.views.append(ChangelogView(page))
            case "/about":
                title.value = "关于"
                drawer.selected_index = 6
                page.views.append(AboutView(page))
            case _:
                pass

        # 在顶部insert自定义appbar和drawer
        page.views[0].drawer = drawer
        page.views[0].padding = ft.Padding.all(0)
        page.views[0].controls.insert(
            0,
            MenuBar(
                bar_height=50,
                bar_title=title,
                bar_bgcolor=ft.Colors.PINK_ACCENT_200,
                on_drawer_click=handle_show_drawer,
                on_min_click=handle_minimized_window,
                on_close_click=handle_close_window
            )
        )

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.on_keyboard_event = handle_keyboard

    await on_mount()

    route_change(page.route)
