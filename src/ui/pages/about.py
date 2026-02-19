import flet as ft
from flet import AppBar, NavigationDrawer
from src.utils import resource_path, __version__ as version


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):

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
            ft.Button(content="GitHub仓库"),
            ft.Button(content="作者主页"),
            ft.Button(content="问题反馈")
        ]
    )

    return ft.View(
        route="/about",
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            logo,
            title,
            ver,
            actions
        ],
        appbar=appbar,
        drawer=drawer
    )
