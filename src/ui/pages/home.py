import flet as ft
import pyautogui
import asyncio
from flet import Page, AppBar, NavigationDrawer
from src.utils import logger


def main(page: Page, appbar: AppBar, drawer: NavigationDrawer):
    _, height = pyautogui.size()
    list_tile_list: list[ft.Column] = []

    async def handle_context_click(e: ft.Event[ft.PopupMenuItem]):
        if e.control.content == "复制":
            await ft.Clipboard().set(e.control.data)
            page.show_dialog(ft.SnackBar(f"已复制 {e.control.data}"))
        if e.control.content == "移除":
            index = [i for i, item in enumerate(list_tile_list) if item.data["title"] == e.control.data["title"] and item.data["subtitle"] == e.control.data["subtitle"]]
            list_tile_list.pop(index[0])
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
        for i in range(0, 100):
            col = ft.Column(
                data={"title": f"nickname_{i}", "subtitle": "song name"},
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
                        title=f"nickname_{i}",
                        subtitle="song name",
                        trailing=create_menu({"title": f"nickname_{i}", "subtitle": "song name"})
                    ),
                ]
            )
            if i < 99:
                col.controls.append(ft.Divider())

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
