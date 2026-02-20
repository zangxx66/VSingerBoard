import flet as ft
from flet import Ref


def douyin_container(page: ft.Page):

    room_id_text = Ref[ft.TextField]()
    sing_prefix_text = Ref[ft.TextField]()
    sing_cd_text = Ref[ft.TextField]()
    fans_lv_text = Ref[ft.TextField]()

    def create_form():
        return ft.Card(
            content=ft.Row(
                wrap=True,
                controls=[
                    ft.TextField(label="房间号", ref=room_id_text, input_filter=ft.InputFilter(regex_string=r"^[1-9]\d*$")),
                    ft.TextField(label="点歌指令", ref=sing_prefix_text),
                    ft.TextField(label="点歌cd", ref=sing_cd_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.TextField(label="粉团等级", ref=fans_lv_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.Button(content="保存")
                ]
            )
        )

    return ft.Container(
        content=create_form()
    )
