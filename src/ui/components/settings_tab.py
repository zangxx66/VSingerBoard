import flet as ft
from flet import Ref
from src.utils import globalfigItem, setup_autostart, async_worker
from src.database import Db as db
from src.ui.components.progress import NProgress


def settings_container(page: ft.Page):

    id_text = Ref[ft.TextField]()
    notify_switch = Ref[ft.Switch]()
    update_switch = Ref[ft.Switch]()
    startup_switch = Ref[ft.Switch]()
    nprogress = NProgress(page)

    async def on_save_click(e: ft.Event[ft.Button]):
        """
        保存设置
        """
        data = globalfigItem(
            id=int(id_text.current.value),
            check_update=notify_switch.current.value,
            startup=startup_switch.current.value
        )
        startup_result = setup_autostart(data.check_update)
        if not startup_result:
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text("开机启动设置失败"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())]
            ))
            return
        result = await async_worker.run_db_operation(db.add_or_update_gloal_config(**data.__dict__))
        if result > 0:
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text("保存成功"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())],
            ))
        else:
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text("保存失败"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())],
            ))

    def create_form():
        """
        生成表单
        """
        return ft.Card(
            content=ft.Row(
                wrap=True,
                controls=[
                    ft.TextField(label="id", ref=id_text, visible=False),
                    ft.Switch(label="桌面通知", ref=notify_switch, value=False),
                    ft.Switch(label="自动检查更新", ref=update_switch, value=False),
                    ft.Switch(label="开机启动", ref=startup_switch, value=False),
                    ft.Button("保存", style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PRIMARY_FIXED_DIM), on_click=on_save_click)
                ]
            )
        )

    async def on_mount():
        nprogress.start()
        data = await async_worker.run_db_operation(db.get_gloal_config())
        if data:
            id_text.current.value = data.id
            notify_switch.current.value = data.notification
            update_switch.current.value = data.check_update
            startup_switch.current.value = data.startup
            page.update()
        nprogress.stop()

    page.run_task(on_mount)

    return ft.Container(
        content=create_form()
    )
