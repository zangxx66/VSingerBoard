import flet as ft
import flet_datatable2 as ftd
from flet import Ref
from src.utils import BiliCredentialItem


def bilibili_container(page: ft.Page):

    room_id_text = Ref[ft.TextField]()
    modal_lv_text = Ref[ft.TextField]()
    user_lv_text = Ref[ft.TextField]()
    sing_prefix_text = Ref[ft.TextField]()
    sing_cd_text = Ref[ft.TextField]()

    def create_form():
        return ft.Container(
            margin=ft.Margin.all(12),
            content=ft.Row(
                wrap=True,
                controls=[
                    ft.TextField(label="房间号", ref=room_id_text, input_filter=ft.InputFilter(regex_string=r"^[1-9]\d*$")),
                    ft.TextField(label="粉丝牌等级", ref=modal_lv_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.TextField(label="用户等级", ref=user_lv_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.TextField(label="点歌指令", ref=sing_prefix_text),
                    ft.TextField(label="点歌cd", ref=sing_cd_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.Button(content="保存")
                ]
            )
        )

    def create_actions():
        return ft.Container(
            padding=ft.Padding(left=24),
            content=ft.Column(
                controls=[
                    ft.Button(icon=ft.Icons.ADD, content="新建账号"),
                    ft.Text(value="未登录账号无法获取到弹幕用户昵称等信息，如有需要可添加一个小号",
                            size=20,
                            text_align=ft.TextAlign.CENTER,
                            )
                ]
            )
        )

    data_table: ftd.DataTable2 | None = None
    credential_list: list[BiliCredentialItem] = []

    credential_list.append(BiliCredentialItem(
        id=1,
        sessdata="",
        bili_jct="",
        buvid3="",
        buvid4="",
        dedeuserid="",
        ac_time_value="",
        uid=1,
        enable=True
    ))

    def generate_columns():
        return [
            ftd.DataColumn2(label="uid", heading_row_alignment=ft.MainAxisAlignment.START),
            ftd.DataColumn2(label="是否启用"),
            ftd.DataColumn2(label="操作")
        ]

    def generate_rows():
        data_rows = []
        for item in credential_list:
            data_rows.append(
                ftd.DataRow2(
                    specific_row_height=50,
                    cells=[
                        ft.DataCell(content=ft.Text(item.uid)),
                        ft.DataCell(content=ft.Text("启用" if item.enable else "禁用")),
                        ft.DataCell(content=ft.Row(controls=[
                            ft.Button(icon=ft.Icons.REFRESH, content="启用/禁用", color=ft.Colors.GREEN_200),
                            ft.Button(icon=ft.Icons.DELETE, content="删除", color=ft.Colors.RED)
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
        rows=generate_rows()
    )

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
