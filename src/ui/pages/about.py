import flet as ft
from flet import AppBar, NavigationDrawer
from src.utils import resource_path, __version__ as version


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):
    url_launcher = ft.UrlLauncher()

    async def handle_click(e: ft.Event[ft.Button]):
        if e.control.data == "feedback":
            await url_launcher.launch_url("https://github.com/zangxx66/VSingerBoard/issues")
        elif e.control.data == "github":
            await url_launcher.launch_url("https://github.com/zangxx66/VSingerBoard")
        else:
            await url_launcher.launch_url("https://space.bilibili.com/909267")

    logo = ft.Container(
        content=ft.Image(src=resource_path("icons/logo.png"), width=128, height=128)
    )

    title = ft.Container(
        content=ft.Text(value="点歌姬", size=20)
    )

    ver = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Text(value=f"v{version}"),
            ft.Button(icon=ft.Icons.CHECK, content="检查更新", style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PRIMARY_FIXED_DIM))
        ]
    )

    actions = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Button(icon=ft.Icons.CODE, content="GitHub仓库", data="github", style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.BLACK_38, color=ft.Colors.WHITE), on_click=handle_click),
            ft.Button(icon=ft.Icons.HOME_FILLED, content="作者主页", data="bilibili", style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PINK_ACCENT_200, color=ft.Colors.WHITE), on_click=handle_click),
            ft.Button(icon=ft.Icons.FEEDBACK, content="问题反馈", data="feedback", style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE), on_click=handle_click)
        ]
    )

    return ft.View(
        route="/about",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            logo,
            title,
            ver,
            actions
        ],
        appbar=appbar,
        drawer=drawer
    )
