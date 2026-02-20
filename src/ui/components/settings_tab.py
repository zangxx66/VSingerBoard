import flet as ft
from flet import Ref


def settings_container(page: ft.Page):

    dark_switch = Ref[ft.Switch]()
    notify_switch = Ref[ft.Switch]()
    update_switch = Ref[ft.Switch]()
    startup_switch = Ref[ft.Switch]()

    def create_form():
        return ft.Card(
            content=ft.Row(
                wrap=True,
                controls=[
                    ft.Switch(label="黑暗模式", ref=dark_switch, value=False),
                    ft.Switch(label="桌面通知", ref=notify_switch, value=False),
                    ft.Switch(label="自动检查更新", ref=update_switch, value=False),
                    ft.Switch(label="开机启动", ref=startup_switch, value=False),
                ]
            )
        )

    return ft.Container(
        content=create_form()
    )
