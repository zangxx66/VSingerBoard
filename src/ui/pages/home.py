import flet as ft


def main(title, appbar, drawer):
    return ft.View(
        route="/",
        controls=[
            ft.Text(title)
        ],
        appbar=appbar,
        drawer=drawer,
        scroll="auto"
    )
