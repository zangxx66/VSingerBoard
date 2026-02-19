import pyautogui
import flet as ft
from flet import AppBar, NavigationDrawer
from .components import bilibili_tab, douyin_tab, settings_tab


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):
    _, height = pyautogui.size()

    return ft.View(
        route="/settings",
        controls=[
            ft.Card(
                content=ft.Tabs(
                    length=3,
                    content=ft.Column(
                        controls=[
                            ft.TabBar(
                                tabs=[
                                    ft.Tab(label="哔哩哔哩设置"),
                                    ft.Tab(label="抖音设置"),
                                    ft.Tab(label="应用设置")
                                ]
                            ),
                            ft.TabBarView(
                                height=int(height * .8),
                                controls=[
                                    bilibili_tab.bilibili_container(page),
                                    douyin_tab.douyin_container(page),
                                    settings_tab.settings_container(page)
                                ]
                            )
                        ]
                    )
                )
            )
        ],
        appbar=appbar,
        drawer=drawer
    )
