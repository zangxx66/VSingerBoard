import flet as ft
import pyautogui
import asyncio
from flet import Page, AppBar, NavigationDrawer
from src.utils import DanmuInfo


def main(page: Page, appbar: AppBar, drawer: NavigationDrawer):
    _, height = pyautogui.size()
    list_tile_list: list[ft.Column] = []
    danmaku_list: list[DanmuInfo] = []

    def on_message(msg):
        global danmaku_list
        danmaku_list = msg

    page.pubsub.subscribe(on_message)

    async def handle_context_click(e: ft.Event[ft.PopupMenuItem]):
        if e.control.content == "复制":
            await ft.Clipboard().set(e.control.data)
            page.show_dialog(ft.SnackBar(f"已复制 {e.control.data}"))
        if e.control.content == "移除":
            index = [i for i, item in enumerate(danmaku_list) if item.data["title"] == e.control.data["title"] and item.data["subtitle"] == e.control.data["subtitle"]]
            # list_tile_list.pop(index[0])
            danmaku_list.pop(index[0])
            page.update()
            page.show_dialog(ft.SnackBar("已移除"))

    def create_menu(data):
        menu = ft.ContextMenu(
            content=ft.IconButton(ft.Icons.MORE_VERT, on_click=lambda e: asyncio.create_task(menu.open())),
            items=[
                ft.PopupMenuItem(
                    content="复制",
                    data=data["subtitle"],
                    on_click=handle_context_click
                ),
                ft.PopupMenuItem(
                    content="移除",
                    data=data,
                    on_click=handle_context_click
                )
            ]
        )
        return menu

    def generate_list():
        for item in danmaku_list:
            col = ft.Column(
                data={"title": item["uname"], "subtitle": item["msg"]},
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
                        title=item["uname"],
                        subtitle=item["msg"],
                        trailing=create_menu({"title": item["uname"], "subtitle": item["msg"]})
                    ),
                ]
            )

            list_tile_list.append(col)
        return list_tile_list

    def create_list_view():
        return ft.ListView(
            spacing=10,
            padding=20,
            scroll="auto",
            controls=generate_list()
        )

    def create_main_card():
        return ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            bgcolor=ft.Colors.WHITE,
            height=int(height * .7),
            content=create_list_view()
        )

    def create_bottom_card():
        return ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            shape=ft.RoundedRectangleBorder(radius=4),
            height=50,
            bgcolor=ft.Colors.WHITE,
            align=ft.Alignment.CENTER,
            content=ft.Row(
                margin=ft.Margin(left=24),
                controls=[
                    ft.Button(icon=ft.Icons.EDIT, bgcolor=ft.Colors.CYAN, color=ft.Colors.WHITE, content="手动点歌"),
                    ft.Button(icon=ft.Icons.DOWNLOAD, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE, content="导出列表"),
                    ft.Button(icon=ft.Icons.DELETE, bgcolor=ft.Colors.RED_ACCENT_400, color=ft.Colors.WHITE, content="清除列表")
                ]
            )
        )

    return ft.View(
        route="/",
        controls=[
            create_main_card(),
            create_bottom_card()
        ],
        appbar=appbar,
        drawer=drawer,
    )
