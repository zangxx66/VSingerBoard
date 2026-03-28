import flet as ft
import flet_datatable2 as ftd
from flet import Ref
from typing import Sequence
from ..controls import NProgress, DataTable
from src.utils import async_worker
from src.database import Db as db


def main(page: ft.Page):
    height = page.window.height

    query_type_text = Ref[ft.Dropdown]()
    source_text = Ref[ft.Dropdown]()
    days_text = Ref[ft.Dropdown]()
    data_table: DataTable | None = None

    async def handle_search_click(e: ft.Event[ft.Button]):
        """
        加载数据
        """
        NProgress.start(page)

        if source_text.current.value == "哔哩哔哩":
            source = "bilibili"
        elif source_text.current.value == "抖音":
            source = "douyin"
        elif source_text.current.value == "全部":
            source = None

        query_type = (
            "song" if query_type_text.current.value == "最受欢迎的歌" else "user"
        )

        if days_text.current.value == "最近3天":
            days = 3
        elif days_text.current.value == "最近5天":
            days = 5
        elif days_text.current.value == "最近7天":
            days = 7
        elif days_text.current.value == "最近15天":
            days = 15
        elif days_text.current.value == "最近30天":
            days = 30

        result = await async_worker.run_db_operation(
            db.get_statisitic(query_type, days, source)
        )
        data_table.rows = generate_rows(result)
        NProgress.stop(page)
        page.update()

    def handle_query_change(e: ft.Event[ft.Dropdown]):
        query_type_text.current.value = e.control.value
        if len(data_table.rows) > 0:
            data_table.rows.clear()
        if e.control.value == "最受欢迎的歌":
            data_table.columns[1].visible = False
            data_table.columns[2].visible = True
        else:
            data_table.columns[1].visible = True
            data_table.columns[2].visible = False
        data_table.update()

    def handle_source_change(e: ft.Event[ft.Dropdown]):
        source_text.current.value = e.control.value

    def handle_days_change(e: ft.Event[ft.Dropdown]):
        days_text.current.value = e.control.value

    def generate_columns():
        """
        生成列
        """
        return [
            ftd.DataColumn2(
                label=ft.Text("平台"), heading_row_alignment=ft.MainAxisAlignment.CENTER
            ),
            ftd.DataColumn2(
                label=ft.Text("昵称"), heading_row_alignment=ft.MainAxisAlignment.CENTER, visible=False
            ),
            ftd.DataColumn2(
                label=ft.Text("歌名"), heading_row_alignment=ft.MainAxisAlignment.CENTER, visible=True
            ),
            ftd.DataColumn2(
                label=ft.Text("次数"), heading_row_alignment=ft.MainAxisAlignment.CENTER
            ),
            ftd.DataColumn2(
                label=ft.Text("日期"), heading_row_alignment=ft.MainAxisAlignment.CENTER
            ),
        ]

    def generate_rows(query_result: Sequence[dict]):
        """
        生成行
        """
        data_rows = []
        for item in query_result:
            data_rows.append(
                ftd.DataRow2(
                    cells=[
                        ft.DataCell(content=ft.Text("哔哩哔哩" if item["source"] == "bilibili" else "抖音")),
                        ft.DataCell(content=ft.Text(item["uname"] if query_type_text.current.value == "点歌最多的人" else item["song_name"])),
                        ft.DataCell(content=ft.Text(item["count"])),
                        ft.DataCell(content=ft.Text(item["day"])),
                    ],
                )
            )
        return data_rows

    data_table = DataTable(
        heading_row_color=ft.Colors.SECONDARY_CONTAINER,
        bottom_margin=10,
        columns=generate_columns(),
        rows=[],
    )

    def create_search_container():
        """
        查询 Container
        """
        return ft.Card(
            margin=ft.Margin.only(left=10, right=10, top=10),
            content=ft.Row(
                controls=[
                    ft.Dropdown(
                        label="查询类型",
                        ref=query_type_text,
                        value="最受欢迎的歌",
                        options=[
                            ft.DropdownOption(
                                key="最受欢迎的歌", content=ft.Text("最受欢迎的歌")
                            ),
                            ft.DropdownOption(
                                key="点歌最多的人", content=ft.Text("点歌最多的人")
                            ),
                        ],
                        on_select=handle_query_change,
                    ),
                    ft.Dropdown(
                        label="平台",
                        ref=source_text,
                        value="全部",
                        options=[
                            ft.DropdownOption(key="全部", content=ft.Text("全部")),
                            ft.DropdownOption(
                                key="哔哩哔哩", content=ft.Text("哔哩哔哩")
                            ),
                            ft.DropdownOption(key="抖音", content=ft.Text("抖音")),
                        ],
                        on_select=handle_source_change,
                    ),
                    ft.Dropdown(
                        label="查询周期",
                        ref=days_text,
                        value="最近3天",
                        options=[
                            ft.DropdownOption(
                                key="最近3天", content=ft.Text("最近3天")
                            ),
                            ft.DropdownOption(
                                key="最近5天", content=ft.Text("最近5天")
                            ),
                            ft.DropdownOption(
                                key="最近7天", content=ft.Text("最近7天")
                            ),
                            ft.DropdownOption(
                                key="最近15天", content=ft.Text("最近15天")
                            ),
                            ft.DropdownOption(
                                key="最近30天", content=ft.Text("最近30天")
                            ),
                        ],
                        on_select=handle_days_change,
                    ),
                    ft.Button(
                        icon=ft.Icons.SEARCH,
                        bgcolor=ft.Colors.PRIMARY_FIXED_DIM,
                        content="查询",
                        on_click=handle_search_click,
                    ),
                ]
            ),
        )

    return ft.View(
        route="/statistic",
        controls=[
            create_search_container(),
            ft.Divider(),
            ft.Card(
                content=data_table,
                height=int(height * 0.8),
                margin=ft.Margin.only(left=10, right=10),
            ),
        ],
    )
