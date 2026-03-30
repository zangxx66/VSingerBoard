import flet as ft
from typing import Optional, Union
from flet import ColorValue, Text, ControlEventHandler


def MenuBar(
    bar_height: Union[int, float],
    bar_title: str | Text = None,
    bar_bgcolor: ColorValue = None,
    on_drawer_click: Optional[ControlEventHandler[ft.IconButton]] = None,
    on_min_click: Optional[ControlEventHandler[ft.IconButton]] = None,
    on_close_click: Optional[ControlEventHandler[ft.IconButton]] = None,
):
    """
    自定义AppBar

    Args:
        bar_height: AppBar 高度
        bar_title: AppBar 标题
        bar_bgcolor: AppBar 背景颜色
        on_drawer_click: 点击抽屉图标事件
        on_min_click: 最小化事件
        on_close_click: 关闭事件

    Returns:
        ft.Row
    """
    return ft.Row(
        height=bar_height if bar_height else 50,
        spacing=0,
        controls=[
            ft.Container(
                height=bar_height if bar_height else 50,
                padding=ft.Padding.only(left=10),
                bgcolor=bar_bgcolor if bar_bgcolor else ft.Colors.PRIMARY,
                content=ft.IconButton(
                    ft.Icons.MENU,
                    tooltip="打开抽屉导航",
                    on_click=on_drawer_click,
                ),
            ),
            ft.WindowDragArea(
                expand=True,
                content=ft.Container(
                    height=bar_height if bar_height else 50,
                    padding=ft.Padding.only(left=10),
                    alignment=ft.Alignment.CENTER_LEFT,
                    bgcolor=bar_bgcolor if bar_bgcolor else ft.Colors.PRIMARY,
                    content=bar_title,
                ),
            ),
            ft.Container(
                height=bar_height if bar_height else 50,
                padding=ft.Padding.only(right=10),
                bgcolor=bar_bgcolor if bar_bgcolor else ft.Colors.PRIMARY,
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            ft.Icons.MINIMIZE,
                            tooltip="最小化",
                            on_click=on_min_click,
                        ),
                        ft.IconButton(
                            ft.Icons.CLOSE,
                            tooltip="退出",
                            on_click=on_close_click,
                        ),
                    ]
                ),
            ),
        ],
    )
