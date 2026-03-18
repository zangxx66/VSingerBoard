import datetime
import time
import threading
import io
import pandas as pd
import flet as ft
from flet import Ref
from src.database import Db as db
from src.utils import (
    logger,
    async_worker,
    HistoryItem,
    resource_path,
    timespan_to_localtime,
)
from ..components import NProgress, ModernToast


_page = 1
total = 0
songs_rows: list[HistoryItem] = []
sem = threading.Semaphore()


def main(page: ft.Page):
    height = page.window.height

    song_name_text = Ref[ft.TextField]()
    uname_text = Ref[ft.TextField]()
    source_text = Ref[ft.Dropdown]()
    start_date_picker = Ref[ft.DatePicker]()
    end_date_picker = Ref[ft.DatePicker]()
    start_date_text = Ref[ft.TextField]()
    end_date_text = Ref[ft.TextField]()
    list_view = Ref[ft.ListView]()

    today = datetime.datetime.now()

    async def load_data(reload: bool):
        """
        获取数据
        """
        global _page, total, songs_rows
        NProgress.start(page)
        if reload:
            _page = 1
            list_view.current.controls = []
            await list_view.current.scroll_to(offset=0)
        else:
            _page += 1
        uname = uname_text.current.value
        song_name = song_name_text.current.value
        source = source_text.current.value
        if source == "all":
            source = None
        start_time = (
            int(start_date_picker.current.value.timestamp())
            if start_date_picker.current.value
            else None
        )
        end_time = (
            int(end_date_picker.current.value.timestamp())
            if end_date_picker.current.value
            else None
        )
        total, songs = await async_worker.run_db_operation(
            db.get_song_history_page(
                uname, song_name, source, start_time, end_time, _page, 20
            )
        )
        if reload:
            songs_rows = songs
        else:
            songs_rows.extend(songs)
        list_view.current.controls = generate_list(songs_rows)
        NProgress.stop(page)
        page.update()

    async def handle_scroll(e: ft.OnScrollEvent):
        """
        滚动到底部加载
        """
        if (
            e.pixels >= e.max_scroll_extent and len(songs_rows) < total and sem.acquire(blocking=False)
        ):
            try:
                await load_data(False)
            finally:
                sem.release()

    def handle_source_change(e: ft.Event[ft.Dropdown]):
        """
        下拉菜单事件
        """
        source_text.current.value = e.control.value

    def handle_start_date_change(e: ft.Event[ft.DatePicker]):
        """
        选择时间事件
        """
        time_array = time.localtime(int(e.control.value.timestamp()))
        other_style_time = time.strftime("%Y-%m-%d", time_array)
        start_date_text.current.value = other_style_time

    def handle_end_date_change(e: ft.Event[ft.DatePicker]):
        """
        选择时间事件
        """
        time_array = time.localtime(int(e.control.value.timestamp()))
        other_style_time = time.strftime("%Y-%m-%d", time_array)
        end_date_text.current.value = other_style_time

    async def handle_search_click(e: ft.Event[ft.Button]):
        """
        搜索
        """
        await load_data(True)

    async def handle_export_click(e: ft.Event[ft.Button]):
        """
        导出列表
        """
        try:
            uname = uname_text.current.value
            song_name = song_name_text.current.value
            source = source_text.current.value
            if source == "all":
                source = None
            start_time = (
                int(start_date_picker.current.value.timestamp())
                if start_date_picker.current.value
                else None
            )
            end_time = (
                int(end_date_picker.current.value.timestamp())
                if end_date_picker.current.value
                else None
            )
            _, songs = await async_worker.run_db_operation(
                db.get_song_history_page(
                    uname, song_name, source, start_time, end_time, 1, total
                )
            )

            df_dict = {
                "日期": [timespan_to_localtime(item.create_time) for item in songs],
                "昵称": [item.uname for item in songs],
                "歌名": [item.song_name for item in songs],
                "平台": [item.source for item in songs],
            }
            df = pd.DataFrame(df_dict)
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer) as writer:
                df.to_excel(writer, sheet_name="Sheet1")
            excel_bytes = excel_buffer.getvalue()
            file_name = f"点歌历史记录_{int(time.time())}"
            select_path = await ft.FilePicker().save_file(
                file_name=file_name,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx"],
                src_bytes=excel_bytes,
            )
            if not select_path:
                ModernToast.info(page, "取消导出")
                return
            ModernToast.success(page, "导出成功")
        except Exception as ex:
            logger.error(f"export history error:{ex}")
            ModernToast.error(page, "导出记录错误")

    start_dp = ft.DatePicker(
        current_date=today, ref=start_date_picker, on_change=handle_start_date_change
    )

    end_dp = ft.DatePicker(
        current_date=today, ref=end_date_picker, on_change=handle_end_date_change
    )

    def create_search_container():
        """
        搜索 container
        """
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.TextField(label="歌名", ref=song_name_text),
                    ft.TextField(label="昵称", ref=uname_text),
                    ft.Dropdown(
                        label="平台",
                        ref=source_text,
                        value="all",
                        options=[
                            ft.DropdownOption(
                                key="bilibili", content=ft.Text("哔哩哔哩")
                            ),
                            ft.DropdownOption(key="douyin", content=ft.Text("抖音")),
                            ft.DropdownOption(key="all", content=ft.Text("全部")),
                        ],
                        on_select=handle_source_change,
                    ),
                    ft.TextField(
                        label="开始时间",
                        value="",
                        ref=start_date_text,
                        on_click=lambda e: page.show_dialog(start_dp),
                    ),
                    ft.TextField(
                        label="结束时间",
                        value="",
                        ref=end_date_text,
                        on_click=lambda e: page.show_dialog(end_dp),
                    ),
                    ft.Button(
                        icon=ft.Icons.SEARCH,
                        style=ft.ButtonStyle(
                            shape=ft.ContinuousRectangleBorder(radius=30),
                            bgcolor=ft.Colors.PRIMARY_FIXED_DIM,
                        ),
                        content="搜索",
                        on_click=handle_search_click,
                    ),
                ]
            )
        )

    def generate_list(songs: list[HistoryItem]):
        """
        生成列表
        """
        col_list = []
        for item in songs:
            img_src = resource_path(f"images/{item.source}.png")
            col = ft.Column(
                controls=[
                    ft.ListTile(
                        leading=ft.Image(src=img_src, width=128, height=128),
                        title=ft.Text(item.uname),
                        subtitle=ft.Text(item.song_name),
                        trailing=ft.Text(timespan_to_localtime(item.create_time)),
                    )
                ]
            )
            col_list.append(col)
        return col_list

    def create_main_card():
        """
        创建主视图
        """
        return ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            height=int(height * 0.65),
            content=ft.ListView(
                ref=list_view,
                on_scroll=handle_scroll,
                divider_thickness=1,
                spacing=10,
                scroll="auto",
                controls=[],
            ),
        )

    def create_actions():
        """
        创建底部按钮
        """
        return ft.Container(
            height=50,
            align=ft.Alignment.CENTER,
            content=ft.Row(
                margin=ft.Margin(left=24),
                controls=[
                    ft.Button(
                        icon=ft.Icons.DOWNLOAD,
                        style=ft.ButtonStyle(
                            shape=ft.ContinuousRectangleBorder(radius=30),
                            bgcolor=ft.Colors.PINK_50,
                        ),
                        content="导出历史记录",
                        on_click=handle_export_click,
                    )
                ],
            ),
        )

    page.run_task(load_data, True)

    return ft.View(
        route="/history",
        controls=[
            create_search_container(),
            ft.Divider(),
            create_main_card(),
            ft.Divider(),
            create_actions(),
        ],
    )
