import flet as ft
from flet import Ref
from src.utils import globalfigItem, setup_autostart, async_worker
from src.database import Db as db


def settings_container(page: ft.Page):

    id_text = Ref[ft.TextField]()
    dark_switch = Ref[ft.Switch]()
    notify_switch = Ref[ft.Switch]()
    update_switch = Ref[ft.Switch]()
    startup_switch = Ref[ft.Switch]()

    async def on_save_click(e: ft.Event[ft.Button]):
        data = globalfigItem(
            id=int(id_text.current.value),
            dark_mode=dark_switch.current.value,
            check_update=notify_switch.current.value,
            startup=startup_switch.current.value
        )
        startup_result = setup_autostart(data.check_update)
        if not startup_result:
            page.show_dialog(ft.AlertDialog(
                icon=ft.Icons.INFO,
                title=ft.Text("提示"),
                content=ft.Text("开机启动设置失败"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())]
            ))
            return
        result = await async_worker.run_db_operation(db.add_or_update_gloal_config(**data.__dict__))
        if result > 0:
            page.show_dialog(ft.AlertDialog(
                icon=ft.Icons.INFO,
                title=ft.Text("提示"),
                content=ft.Text("保存成功"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())],
            ))
        else:
            page.show_dialog(ft.AlertDialog(
                icon=ft.Icons.INFO,
                title=ft.Text("提示"),
                content=ft.Text("保存失败"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())],
            ))

    def create_form():
        return ft.Card(
            content=ft.Row(
                wrap=True,
                controls=[
                    ft.TextField(label="id", ref=id_text, visible=False),
                    ft.Switch(label="黑暗模式", ref=dark_switch, value=False),
                    ft.Switch(label="桌面通知", ref=notify_switch, value=False),
                    ft.Switch(label="自动检查更新", ref=update_switch, value=False),
                    ft.Switch(label="开机启动", ref=startup_switch, value=False),
                    ft.Button("保存", on_click=on_save_click)
                ]
            )
        )

    async def on_mount():
        data = await async_worker.run_db_operation(db.get_gloal_config())
        if data:
            id_text.current.value = data.id
            dark_switch.current.value = data.dark_mode
            notify_switch.current.value = data.notification
            update_switch.current.value = data.check_update
            startup_switch.current.value = data.startup
            page.update()

    page.run_task(on_mount)

    return ft.Container(
        content=create_form()
    )
