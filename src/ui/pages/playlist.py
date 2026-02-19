import time
import pyautogui
import flet_datatable2 as ftd
import flet as ft
from flet import AppBar, NavigationDrawer, Ref
from src.utils import PlaylistItem


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):
    _, height = pyautogui.size()

    keyword_text = Ref[ft.TextField]()
    data_table: ftd.DataTable2 | None = None
    playlist_list: list[PlaylistItem] = []

    for i in range(0, 100):
        playlist_list.append(PlaylistItem(
            id=i,
            song_name=f"song_name_{i}",
            singer=f"singer_{i}",
            is_sc=i % 2 == 0,
            sc_price=30 if i % 2 == 0 else 0,
            language="",
            tag="",
            create_time=int(time.time())
        ))

    def generate_colmns():
        return [
            ftd.DataColumn2(label=ft.Text("歌名"), size=ftd.DataColumnSize.L, heading_row_alignment=ft.MainAxisAlignment.START),
            ftd.DataColumn2(label=ft.Text("歌手"), heading_row_alignment=ft.MainAxisAlignment.START),
            ftd.DataColumn2(label=ft.Text("语种"), heading_row_alignment=ft.MainAxisAlignment.START),
            ftd.DataColumn2(label=ft.Text("标签"), heading_row_alignment=ft.MainAxisAlignment.START),
            ftd.DataColumn2(label=ft.Text("SC曲目价格"), numeric=True, heading_row_alignment=ft.MainAxisAlignment.START),
            ftd.DataColumn2(label="操作")
        ]

    def generate_rows():
        data_rows = []
        for item in playlist_list:
            data_rows.append(
                ftd.DataRow2(
                    specific_row_height=50,
                    cells=[
                        ft.DataCell(content=ft.Text(item.song_name)),
                        ft.DataCell(content=ft.Text(item.singer)),
                        ft.DataCell(content=ft.Text(item.language)),
                        ft.DataCell(content=ft.Text(item.tag)),
                        ft.DataCell(content=ft.Text(item.sc_price)),
                        ft.DataCell(content=ft.Row(controls=[
                            ft.Button(icon=ft.Icons.EDIT, content="编辑", color=ft.Colors.GREEN),
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
        columns=generate_colmns(),
        rows=generate_rows()
    )

    def handle_search_click(e: ft.Event[ft.Button]):
        page.show_dialog(ft.SnackBar(content=keyword_text.current.value))

    def create_search_container():
        return ft.Card(
            content=ft.Row(
                controls=[
                    ft.TextField(label="关键词", ref=keyword_text),
                    ft.Button(icon=ft.Icons.SEARCH, content="搜索", on_click=handle_search_click)
                ]
            )
        )

    def create_action_container():
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(icon=ft.Icons.ADD, content="新建歌曲"),
                    ft.Button(icon=ft.Icons.UPLOAD, content="导入歌单"),
                    ft.Button(icon=ft.Icons.DOWNLOAD, content="导出歌单")
                ]
            )
        )

    return ft.View(
        route="/playlist",
        controls=[
            create_search_container(),
            ft.Divider(),
            create_action_container(),
            ft.Divider(),
            ft.Card(
                content=data_table,
                height=int(height * .7)
            )
        ],
        appbar=appbar,
        drawer=drawer
    )
