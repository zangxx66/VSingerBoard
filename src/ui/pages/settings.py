import flet as ft


def main(title, appbar, drawer):
    return ft.View(
        route="/settings",
        controls=[
            ft.Text(title)
        ],
        appbar=appbar,
        drawer=drawer
    )
