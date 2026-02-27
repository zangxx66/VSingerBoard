import flet as ft


class NProgress():
    def __init__(self, page: ft.Page):
        self._page = page

    def start(self):
        self._page.overlay.append(
            ft.Stack(
                controls=[
                    ft.Container(expand=True, bgcolor=ft.Colors.WHITE, opacity=0.8),
                    ft.Column(
                        controls=[ft.ProgressRing()],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        align=ft.Alignment.CENTER
                    ),
                ]
            )
        )
        self._page.update()

    def stop(self):
        self._page.overlay.clear()
        self._page.update()
