import time
import pyautogui
import io
import pandas as pd
import flet_datatable2 as ftd
import flet as ft
from flet import AppBar, NavigationDrawer, Ref
from src.utils import PlaylistItem, async_worker, logger
from src.database import Db as db
from src.ui.components.progress import NProgress


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):
    _, height = pyautogui.size()

    keyword_text = Ref[ft.TextField]()
    data_table: ftd.DataTable2 | None = None
    nprogress = NProgress(page)

    _page = Ref[ft.Text]()
    pages_num = 0
    total = 0

    async def load_data():
        nonlocal pages_num, total
        nprogress.start()
        keyword = keyword_text.current.value if keyword_text.current else None
        count, songs = await async_worker.run_db_operation(
            db.get_playlist_page(keyword, _page.current.value, 20)
        )
        total = count
        pages_num = (count + 20 - 1) // 20
        data_table.rows = generate_rows(songs)
        nprogress.stop()
        page.update()

    async def set_page(p=None, delta=0):
        nonlocal _page
        if p is not None:
            _page.current.value = p
        elif delta:
            _page.current.value += delta
        else:
            return
        await load_data()

    async def next_page(e):
        if _page.current.value < pages_num:
            await set_page(delta=1)

    async def prev_page(e):
        if _page.current.value > 1:
            await set_page(delta=-1)

    async def goto_first_page(e):
        if _page.current.value > 1:
            await set_page(p=1)

    async def goto_last_page(e):
        if _page.current.value != pages_num:
            await set_page(p=pages_num)

    def create_paging():
        return ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            shape=ft.RoundedRectangleBorder(radius=4),
            height=50,
            bgcolor=ft.Colors.WHITE,
            align=ft.Alignment.CENTER,
            content=ft.Row(
                margin=ft.Margin(left=24),
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_LEFT,
                        on_click=goto_first_page,
                        tooltip="首页",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_LEFT,
                        on_click=prev_page,
                        tooltip="上一页",
                    ),
                    ft.Text(value=1, ref=_page),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_RIGHT,
                        on_click=next_page,
                        tooltip="下一页",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                        on_click=goto_last_page,
                        tooltip="尾页",
                    ),
                ],
            ),
        )

    def handle_delete_click(e: ft.Event[ft.Button]):
        async def delete():
            id = e.control.data
            result = await async_worker.run_db_operation(db.delete_playlist([id]))
            if result > 0:
                page.pop_dialog()
                page.show_dialog(ft.SnackBar("删除成功"))
                await set_page(p=1)
            else:
                page.pop_dialog()
                page.show_dialog(ft.SnackBar("删除失败"))

        page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("提示"),
                content=ft.Text("是否删除？"),
                actions=[
                    ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                    ft.TextButton(
                        "删除", on_click=lambda ee: async_worker.submit(delete())
                    ),
                ],
            )
        )

    def handle_create_or_edit(e: ft.Event[ft.Button]):
        data = e.control.data
        title = "编辑" if data else "新增"

        async def submit():
            if not song_name.value:
                page.show_dialog(ft.SnackBar("歌名不为空"))
                return
            if is_sc is True:
                if not sc_price.value or int(sc_price.value) < 30:
                    page.show_dialog(ft.SnackBar("SC最少30"))
                    return

            playlist: PlaylistItem = PlaylistItem(
                id=data.id if data else 0,
                song_name=song_name.value,
                singer=singer.value,
                language=language.value,
                tag=tag.value,
                is_sc=bool(is_sc.value),
                sc_price=int(sc_price.value),
                create_time=data.create_time if data else int(time.time()),
            )

            result = await async_worker.run_db_operation(
                db.add_or_update_playlist(**playlist.__dict__)
            )
            msg = f"{title}成功" if result > 0 else f"{title}失败"
            page.show_dialog(ft.SnackBar(msg))
            if result <= 0:
                page.pop_dialog()
                return

            new_rows = ftd.DataRow2(
                data=result,
                specific_row_height=50,
                cells=[
                    ft.DataCell(content=ft.Text(playlist.song_name)),
                    ft.DataCell(content=ft.Text(playlist.singer)),
                    ft.DataCell(content=ft.Text(playlist.language)),
                    ft.DataCell(content=ft.Text(playlist.tag)),
                    ft.DataCell(content=ft.Text(playlist.sc_price)),
                    ft.DataCell(
                        content=ft.Row(
                            controls=[
                                ft.Button(
                                    icon=ft.Icons.EDIT,
                                    data=playlist,
                                    content="编辑",
                                    style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.CYAN, color=ft.Colors.WHITE),
                                    on_click=handle_create_or_edit,
                                ),
                                ft.Button(
                                    icon=ft.Icons.DELETE,
                                    data=playlist.id,
                                    content="删除",
                                    style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
                                    on_click=handle_delete_click,
                                ),
                            ]
                        )
                    ),
                ],
            )

            if data:
                data_table.rows = [
                    new_rows if item.data == data.id else item
                    for item in data_table.rows
                ]
            else:
                data_table.rows.insert(0, new_rows)
            page.pop_dialog()
            page.update()

        page.show_dialog(
            ft.AlertDialog(
                title=title,
                content=ft.Column(
                    height=400,
                    controls=[
                        song_name := ft.TextField(
                            label="歌名", value=data.song_name if data else ""
                        ),
                        singer := ft.TextField(
                            label="歌手", value=data.singer if data else ""
                        ),
                        language := ft.TextField(
                            label="语种", value=data.language if data else ""
                        ),
                        tag := ft.TextField(
                            label="标签", value=data.tag if data else ""
                        ),
                        ft.Text("是否SC歌曲"),
                        is_sc := ft.RadioGroup(
                            value=data.is_sc if data else False,
                            content=ft.Row(
                                controls=[
                                    ft.Radio(label="是", value=True),
                                    ft.Radio(label="否", value=False),
                                ]
                            ),
                        ),
                        sc_price := ft.TextField(
                            label="SC价格",
                            value=data.sc_price if data else 0,
                            input_filter=ft.InputFilter(regex_string=r"^\d+$"),
                        ),
                    ]
                ),
                actions=[
                    ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                    ft.TextButton("提交", on_click=submit),
                ],
            )
        )

    async def handle_import_click(e: ft.Event[ft.Button]):
        nonlocal _page
        files = await ft.FilePicker().pick_files(
            allow_multiple=False,
            with_data=False,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )

        if not files:
            return

        try:
            selected = files[0]
            df = pd.read_excel(
                selected.path,
                na_values="",
                dtype={
                    "歌曲名": str,
                    "歌手": str,
                    "语种": str,
                    "标签": str,
                    "是否SC曲目": str,
                    "SC曲目价格": int,
                },
            )
            import_list: list[PlaylistItem] = []
            for index in range(0, len(df)):
                import_data = {
                    "song_name": df.iloc[index]["歌曲名"],
                    "singer": df.iloc[index]["歌手"],
                    "language": df.iloc[index]["语种"],
                    "tag": df.iloc[index]["标签"] if df.iloc[index]["标签"] else None,
                    "is_sc": True if df.iloc[index]["是否SC曲目"] == "是" else False,
                    "sc_price": (
                        int(df.iloc[index]["SC曲目价格"])
                        if df.iloc[index]["SC曲目价格"]
                        else 0
                    ),
                    "create_time": int(time.time()),
                }
                import_list.append(import_data)
            await async_worker.run_db_operation(db.bulk_add_playlist(import_list))
            page.show_dialog(ft.SnackBar("导入成功"))
            _page.current.value = 1
            await load_data()
        except Exception as ex:
            logger.error(f"import xlsx error:{ex}")
            page.show_dialog(ft.SnackBar("导入xlsx文件错误"))

    async def handle_export_click(e: ft.Event[ft.Button]):
        try:
            keyword = keyword_text.current.value if keyword_text.current else None
            _, songs = await async_worker.run_db_operation(
                db.get_playlist_page(keyword, 1, total)
            )
            df_dict = {
                "歌曲名": [item.song_name for item in songs],
                "歌手": [item.singer for item in songs],
                "语种": [item.language for item in songs],
                "标签": [item.tag for item in songs],
                "是否SC曲目": ["是" if item.is_sc else "否" for item in songs],
                "SC曲目价格": [item.sc_price for item in songs],
            }
            df = pd.DataFrame(df_dict)
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer) as writer:
                df.to_excel(writer, sheet_name="Sheet1")
            excel_bytes = excel_buffer.getvalue()
            file_name = f"歌单_{int(time.time())}"
            select_path = await ft.FilePicker().save_file(
                file_name=file_name,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx"],
                src_bytes=excel_bytes,
            )
            if not select_path:
                page.show_dialog(ft.SnackBar("取消导出"))
                return
            page.show_dialog(ft.SnackBar("导出成功"))
        except Exception as ex:
            logger.error(f"export xlsx error:{ex}")
            page.show_dialog(ft.SnackBar("导出歌单错误"))

    def generate_columns():
        return [
            ftd.DataColumn2(
                label=ft.Text("歌名"),
                size=ftd.DataColumnSize.L,
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
            ),
            ftd.DataColumn2(
                label=ft.Text("歌手"), heading_row_alignment=ft.MainAxisAlignment.CENTER
            ),
            ftd.DataColumn2(
                label=ft.Text("语种"), heading_row_alignment=ft.MainAxisAlignment.CENTER
            ),
            ftd.DataColumn2(
                label=ft.Text("标签"), heading_row_alignment=ft.MainAxisAlignment.CENTER
            ),
            ftd.DataColumn2(
                label=ft.Text("SC曲目价格"),
                numeric=True,
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
            ),
            ftd.DataColumn2(
                label="操作", heading_row_alignment=ft.MainAxisAlignment.CENTER
            ),
        ]

    def generate_rows(playlist_list: list[PlaylistItem]):
        data_rows = []
        for item in playlist_list:
            data_rows.append(
                ftd.DataRow2(
                    data=item.id,
                    specific_row_height=50,
                    cells=[
                        ft.DataCell(content=ft.Text(item.song_name)),
                        ft.DataCell(content=ft.Text(item.singer)),
                        ft.DataCell(content=ft.Text(item.language)),
                        ft.DataCell(content=ft.Text(item.tag)),
                        ft.DataCell(content=ft.Text(item.sc_price)),
                        ft.DataCell(
                            content=ft.Row(
                                controls=[
                                    ft.Button(
                                        icon=ft.Icons.EDIT,
                                        data=item,
                                        content="编辑",
                                        style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.CYAN, color=ft.Colors.WHITE),
                                        on_click=handle_create_or_edit,
                                    ),
                                    ft.Button(
                                        icon=ft.Icons.DELETE,
                                        data=item.id,
                                        content="删除",
                                        style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
                                        on_click=handle_delete_click,
                                    ),
                                ]
                            )
                        ),
                    ],
                )
            )
        return data_rows

    data_table = ftd.DataTable2(
        heading_row_color=ft.Colors.SECONDARY_CONTAINER,
        bottom_margin=10,
        visible_vertical_scroll_bar=True,
        columns=generate_columns(),
        rows=[],
    )

    async def handle_search_click(e: ft.Event[ft.Button]):
        await set_page(p=1)

    def create_search_container():
        return ft.Card(
            content=ft.Row(
                controls=[
                    ft.TextField(label="关键词", ref=keyword_text),
                    ft.Button(
                        icon=ft.Icons.SEARCH,
                        style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PRIMARY_FIXED_DIM, color=ft.Colors.WHITE),
                        content="搜索",
                        on_click=handle_search_click,
                    ),
                ]
            )
        )

    def create_action_container():
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Button(
                        icon=ft.Icons.ADD,
                        style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.CYAN, color=ft.Colors.WHITE),
                        content="新建歌曲",
                        data=None,
                        on_click=handle_create_or_edit,
                    ),
                    ft.Button(
                        icon=ft.Icons.UPLOAD,
                        style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.AMBER, color=ft.Colors.WHITE),
                        content="导入歌单",
                        on_click=handle_import_click,
                    ),
                    ft.Button(
                        icon=ft.Icons.DOWNLOAD,
                        style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                        content="导出歌单",
                        on_click=handle_export_click,
                    ),
                ]
            )
        )

    page.run_task(load_data)

    return ft.View(
        route="/playlist",
        controls=[
            create_search_container(),
            ft.Divider(),
            create_action_container(),
            ft.Divider(),
            ft.Card(content=data_table, height=int(height * 0.6)),
            ft.Divider(),
            create_paging(),
        ],
        appbar=appbar,
        drawer=drawer,
    )
