import base64
import asyncio
import flet as ft
import flet_datatable2 as ftd
from asyncio import Task
from flet import Ref
from bilibili_api.login_v2 import QrCodeLogin, QrCodeLoginChannel
from src.utils import BiliCredentialItem, bconfigItem, async_worker
from src.database import Db as db
from src.live import bili_manager


def bilibili_container(page: ft.Page):

    id_text = Ref[ft.TextField]()
    room_id_text = Ref[ft.TextField]()
    modal_lv_text = Ref[ft.TextField]()
    user_lv_text = Ref[ft.TextField]()
    sing_prefix_text = Ref[ft.TextField]()
    sing_cd_text = Ref[ft.TextField]()

    async def on_save_click(e: ft.Event[ft.Button]):
        data = bconfigItem(
            id=int(id_text.current.value),
            room_id=int(room_id_text.current.value),
            modal_level=int(modal_lv_text.current.value),
            user_level=int(user_lv_text.current.value),
            sing_prefix=sing_prefix_text.current.value,
            sing_cd=int(sing_cd_text.current.value)
        )
        result = await async_worker.run_db_operation(db.add_or_update_bili_config(**data.__dict__))
        if result > 0:
            async_worker.submit(bili_manager.restart())
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
        return ft.Container(
            margin=ft.Margin.all(12),
            content=ft.Row(
                wrap=True,
                controls=[
                    ft.TextField(label="id", ref=id_text, visible=False),
                    ft.TextField(label="房间号", ref=room_id_text, input_filter=ft.InputFilter(regex_string=r"^[1-9]\d*$")),
                    ft.TextField(label="粉丝牌等级", ref=modal_lv_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.TextField(label="用户等级", ref=user_lv_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.TextField(label="点歌指令", ref=sing_prefix_text),
                    ft.TextField(label="点歌cd", ref=sing_cd_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.Button(content="保存", on_click=on_save_click)
                ]
            )
        )

    qr_code_login: QrCodeLogin = None
    login_task: Task = None

    async def get_qr_code():
        global qr_code_login
        qr_code_login = QrCodeLogin(platform=QrCodeLoginChannel.WEB)
        await qr_code_login.generate_qrcode()
        qr_code = qr_code_login.get_qrcode_picture()
        binary_data = qr_code.content
        encoded_string = base64.b64encode(binary_data).decode("utf-8")
        return encoded_string

    async def check_qr_code():
        global qr_code_login, login_task
        if not qr_code_login:
            return
        while not qr_code_login.has_done():
            await asyncio.sleep(2)
        else:
            bili_cred = qr_code_login.get_credential()
            qr_code_login = None
            new_dic = bili_cred.__dict__
            model_fileds = ['ac_time_value', 'bili_jct', 'buvid3', 'buvid4', 'dedeuserid', 'enable', 'id', 'sessdata', 'uid']
            model_dic = {k: v for k, v in new_dic.items() if v is not None and k in model_fileds}
            uid = model_dic["dedeuserid"]
            model_dic["uid"] = uid
            model_dic["enable"] = False
            cred = await async_worker.run_db_operation(db.get_bcredential(uid=uid))
            if not cred:
                await async_worker.run_db_operation(db.add_bcredential(**model_dic))
            else:
                new_dic["enable"] = cred.enable
                await async_worker.run_db_operation(db.update_bcredential(pk=cred.id, **model_dic))
            if login_task and not login_task.cancelled():
                login_task.cancel()
            async_worker.submit(bili_manager.restart())
            page.pop_dialog()

    async def on_add_cred_click(e: ft.Event[ft.Button]):
        global login_task
        img_src = await get_qr_code()
        login_task = asyncio.create_task(check_qr_code())
        page.show_dialog(ft.AlertDialog(
            title=ft.Text("新建账号"),
            content=ft.Image(
                src=img_src,
                width=256,
                height=256,
            ),
            on_dismiss=lambda ee: login_task.cancel(),
            actions=[
                ft.Button("关闭", on_click=lambda ee: page.pop_dialog())
            ]
        ))

    def create_actions():
        return ft.Container(
            padding=ft.Padding(left=24),
            content=ft.Column(
                controls=[
                    ft.Button(icon=ft.Icons.ADD, content="新建账号", on_click=on_add_cred_click),
                    ft.Text(value="未登录账号无法获取到弹幕用户昵称等信息，如有需要可添加一个小号",
                            size=20,
                            text_align=ft.TextAlign.CENTER,
                            )
                ]
            )
        )

    data_table: ftd.DataTable2 | None = None

    def generate_columns():
        return [
            ftd.DataColumn2(label="id", visible=False),
            ftd.DataColumn2(label="uid", heading_row_alignment=ft.MainAxisAlignment.START),
            ftd.DataColumn2(label="是否启用"),
            ftd.DataColumn2(label="操作")
        ]

    def generate_rows(itmes: list[BiliCredentialItem]):
        data_rows = []
        for item in itmes:
            data_rows.append(
                ftd.DataRow2(
                    specific_row_height=50,
                    cells=[
                        ft.DataCell(content=ft.Text(item.id), visible=False),
                        ft.DataCell(content=ft.Text(item.uid)),
                        ft.DataCell(content=ft.Text("启用" if item.enable else "禁用")),
                        ft.DataCell(content=ft.Row(controls=[
                            ft.Button(icon=ft.Icons.REFRESH, content="启用/禁用", color=ft.Colors.GREEN_200, data={"id": item.id, "enable": not item.enable}, on_click=on_status_click),
                            ft.Button(icon=ft.Icons.DELETE, content="删除", color=ft.Colors.RED, data=item.id, on_click=on_delete_click)
                        ]))
                    ]
                )
            )
        return data_rows

    data_table = ftd.DataTable2(
        heading_row_color=ft.Colors.SECONDARY_CONTAINER,
        bottom_margin=10,
        visible_vertical_scroll_bar=True,
        columns=generate_columns(),
        rows=generate_rows([])
    )

    async def on_status_click(e: ft.Event[ft.Button]):
        id = e.control.data["id"]
        enable = e.control.data["enable"]
        result = await async_worker.run_db_operation(db.update_bcredential(pk=id, enable=enable))
        if result > 0:
            page.show_dialog(ft.AlertDialog(
                icon=ft.Icons.INFO,
                title=ft.Text("提示"),
                content=ft.Text("保存成功"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())],
            ))
            async_worker.submit(bili_manager.restart())
            credential_list = await async_worker.run_db_operation(db.get_bcredential_list())
            data_rows = generate_rows(credential_list)
            data_table.rows = data_rows
            page.update()
        else:
            page.show_dialog(ft.AlertDialog(
                icon=ft.Icons.INFO,
                title=ft.Text("提示"),
                content=ft.Text("保存失败"),
                actions=[ft.Button("确定", on_click=lambda ee: page.pop_dialog())],
            ))

    def on_delete_click(e: ft.Event[ft.Button]):
        async def delete():
            id = e.control.data
            result = await async_worker.run_db_operation(db.delete_bcredential(pk=id))
            if result > 0:
                page.show_dialog(ft.SnackBar("删除成功"))
                credential_list = await async_worker.run_db_operation(db.get_bcredential_list())
                data_rows = generate_rows(credential_list)
                data_table.rows = data_rows
                async_worker.submit(bili_manager.restart())
                page.update()
            else:
                page.show_dialog(ft.SnackBar("删除失败"))

        page.show_dialog(ft.AlertDialog(
            title=ft.Text("提示"),
            content=ft.Text("是否删除？"),
            actions=[
                ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                ft.TextButton("删除", on_click=lambda ee: async_worker.submit(delete()))
            ]
        ))

    async def on_mount():
        data = await async_worker.run_db_operation(db.get_bconfig())
        if data:
            id_text.current.value = data.id
            room_id_text.current.value = data.room_id
            modal_lv_text.current.value = data.modal_level
            user_lv_text.current.value = data.user_level
            sing_prefix_text.current.value = data.sing_prefix
            sing_cd_text.current.value = data.sing_cd
        credential_list = await async_worker.run_db_operation(db.get_bcredential_list())
        data_rows = generate_rows(credential_list)
        data_table.rows = data_rows
        page.update()

    page.run_task(on_mount)

    return ft.Container(
        content=ft.Column(
            controls=[
                create_form(),
                ft.Divider(),
                create_actions(),
                ft.Divider(),
                data_table,
            ]
        )
    )
