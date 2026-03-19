import flet as ft
from ..components import bilibili_container, douyin_container, settings_container


def main(page: ft.Page):
    height = page.window.height

    return ft.View(
        route="/settings",
        controls=[
            ft.Card(
                margin=ft.Margin.only(left=10, right=10),
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
                                    bilibili_container(page),
                                    douyin_container(page),
                                    settings_container(page)
                                ]
                            )
                        ]
                    )
                )
            )
        ],
    )
