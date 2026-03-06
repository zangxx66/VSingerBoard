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
            ft.Button(content="检查更新")
        ]
    )

    actions = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Button(content="GitHub仓库", data="github", on_click=handle_click),
            ft.Button(content="作者主页", data="bilibili", on_click=handle_click),
            ft.Button(content="问题反馈", data="feedback", on_click=handle_click)
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
