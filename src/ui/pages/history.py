import datetime
import time
import pyautogui
import flet as ft
from flet import AppBar, NavigationDrawer, Ref
from src.utils import logger


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):
    _, height = pyautogui.size()

    song_name = Ref[ft.TextField]()
    uname = Ref[ft.TextField]()
    source = Ref[ft.Dropdown]()
    start_date_picker = Ref[ft.DatePicker]()
    end_date_picker = Ref[ft.DatePicker]()
    start_date_text = Ref[ft.TextField]()
    end_date_text = Ref[ft.TextField]()

    today = datetime.datetime.now()

    def handle_source_change(e: ft.Event[ft.Dropdown]):
        source.current.value = e.control.value

    def handle_start_date_change(e: ft.Event[ft.DatePicker]):
        time_array = time.localtime(int(e.control.value.timestamp()))
        other_style_time = time.strftime("%Y-%m-%d", time_array)
        start_date_text.current.value = other_style_time

    def handle_end_date_change(e: ft.Event[ft.DatePicker]):
        time_array = time.localtime(int(e.control.value.timestamp()))
        other_style_time = time.strftime("%Y-%m-%d", time_array)
        end_date_text.current.value = other_style_time

    def handle_search_click(e: ft.Event[ft.Button]):
        page.show_dialog(ft.SnackBar(content=f"歌名：{song_name.current.value}, 昵称：{uname.current.value}, 平台: {source.current.value}, 时间： {int(start_date_picker.current.value.timestamp())} - {int(end_date_picker.current.value.timestamp())}"))

    start_dp = ft.DatePicker(
        modal=True,
        current_date=today,
        ref=start_date_picker,
        on_change=handle_start_date_change
    )

    end_dp = ft.DatePicker(
        current_date=today,
        ref=end_date_picker,
        on_change=handle_end_date_change
    )

    def create_search_container():
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.TextField(label="歌名", ref=song_name),
                    ft.TextField(label="昵称", ref=uname),
                    ft.Dropdown(label="平台", ref=source, value="抖音", options=[
                        ft.DropdownOption(key="哔哩哔哩", content=ft.Text("哔哩哔哩")),
                        ft.DropdownOption(key="抖音", content=ft.Text("抖音"))
                    ], on_select=handle_source_change),
                    ft.TextField(label="开始时间", value="", ref=start_date_text, on_click=lambda e: page.show_dialog(start_dp)),
                    ft.TextField(label="结束时间", value="", ref=end_date_text, on_click=lambda e: page.show_dialog(end_dp)),
                    ft.Button(icon=ft.Icons.SEARCH, content="搜索", on_click=handle_search_click)
                ]
            )
        )

    def generate_list():
        col_list = []
        for i in range(0, 100):
            col = ft.Column(
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
                        title=f"nickname_{i}",
                        subtitle="song name"
                    )
                ]
            )
            if i < 99:
                col.controls.append(ft.Divider())

            col_list.append(col)
        return col_list

    def create_main_card():
        return ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            bgcolor=ft.Colors.WHITE,
            height=int(height * .7),
            content=ft.ListView(
                spacing=10,
                scroll="auto",
                controls=generate_list()
            )
        )

    return ft.View(
        route="/history",
        controls=[
            create_search_container(),
            ft.Divider(),
            create_main_card()
        ],
        appbar=appbar,
        drawer=drawer
    )
