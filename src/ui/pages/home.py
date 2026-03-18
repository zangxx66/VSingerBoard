import time
import io
import pandas as pd
import flet as ft
from typing import cast
from src.utils import DanmuInfo, logger, timespan_to_localtime
from src.manager import MessageManager
from ..components import ModernToast


def main(page: ft.Page):
    height = page.window.height
    list_tile_list: list[ft.Column] = []
    danmaku_list: list[DanmuInfo] = []

    message_handler = cast(MessageManager, page.data["message_handler"])

    def on_message(msg):
        """
        更新点歌列表
        """
        nonlocal danmaku_list
        danmaku_list = msg

        def update_ui():
            list_view.controls = generate_list()
            page.update()
        page.run_thread(update_ui)

    message_handler.events.on("on_message_update", on_message)

    async def on_mount():
        """
        初始化数据同步
        """
        await message_handler.sync_current_messages()

    async def handle_context_click(e: ft.Event[ft.IconButton]):
        """
        ContextMenu 事件
        """
        if e.control.data["action"] == "copy":
            await on_copy(e.control.data["msg"])
        if e.control.data["action"] == "delete":
            message_handler.delete_message(
                e.control.data["source"], 
                e.control.data["msg_id"]
            )
            ModernToast.success(page, "已移除")

    async def on_copy(data):
        """
        复制歌名到剪切板
        """
        await ft.Clipboard().set(data)
        ModernToast.success(page, f"已复制 {data}")

    def on_clear(e: ft.Event[ft.Button]):
        """
        清除列表
        """
        if len(danmaku_list) == 0:
            ModernToast.info(page, "没有数据")
            return

        async def do_clear():
            await message_handler.clear_all_messages()
            ModernToast.success(page, "清除列表成功")

        page.run_task(do_clear)

    async def handle_export_click(e: ft.Event[ft.Button]):
        """
        导出列表
        """
        try:
            if len(danmaku_list) == 0:
                ModernToast.info(page, "没有数据")
                return
            df_dict = {
                "日期": [
                    timespan_to_localtime(item.send_time) for item in danmaku_list
                ],
                "昵称": [item.uname for item in danmaku_list],
                "歌名": [item.msg for item in danmaku_list],
                "平台": [item.source for item in danmaku_list],
            }
            df = pd.DataFrame(df_dict)
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer) as writer:
                df.to_excel(writer, sheet_name="Sheet1")
            excel_bytes = excel_buffer.getvalue()
            file_name = f"点歌列表_{time.time()}"
            select_path = await ft.FilePicker().save_file(
                file_name=file_name,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx"],
                src_bytes=excel_bytes,
            )
            if not select_path:
                ModernToast.warning(page, "取消导出")
                return
            ModernToast.success(page, "导出成功")
        except Exception as ex:
            logger.error(f"export xlsx error:{ex}")
            ModernToast.error(page, "导出点歌列表错误")

    def handle_create_click(e: ft.Event[ft.Button]):
        """
        手动插入一条记录到列表
        """

        def submit():
            if not uname.value:
                ModernToast.warning(page, "昵称不为空")
                return
            if not msg.value:
                ModernToast.warning(page, "歌名不为空")
                return

            message_handler.add_manual_message(
                {
                    "source": source.value,
                    "data": DanmuInfo(
                        msg_id=int(time.time()),
                        uid=1,
                        uname=uname.value,
                        msg=msg.value,
                        medal_level=0,
                        medal_name="",
                        guard_level=0,
                        price=0,
                        send_time=int(time.time()),
                        status=0,
                        source=source.value,
                    ),
                },
            )
            page.pop_dialog()

        page.show_dialog(
            ft.AlertDialog(
                title="手动点歌",
                content=ft.Column(
                    height=240,
                    controls=[
                        uname := ft.TextField(label="用户昵称"),
                        msg := ft.TextField(label="点歌内容"),
                        source := ft.Dropdown(
                            label="点歌平台",
                            value="bilibili",
                            options=[
                                ft.DropdownOption(
                                    key="bilibili", content=ft.Text("哔哩哔哩")
                                ),
                                ft.DropdownOption(
                                    key="douyin", content=ft.Text("抖音")
                                ),
                            ],
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                    ft.TextButton("提交", on_click=submit),
                ],
            )
        )

    def generate_list():
        """
        生成列表
        """
        nonlocal list_tile_list
        list_tile_list.clear()
        for item in danmaku_list:
            col = ft.Column(
                data={"title": item.uname, "subtitle": item.msg},
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
                        bgcolor=ft.Colors.PRIMARY_FIXED_DIM,
                        shape=ft.RoundedRectangleBorder(radius=15),
                        title=item.uname,
                        subtitle=item.msg,
                        trailing=ft.Row(
                            tight=True,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.COPY,
                                    data={"action": "copy", "msg": item.msg},
                                    tooltip="复制",
                                    on_click=handle_context_click,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED,
                                    data={
                                        "action": "delete",
                                        "source": item.source,
                                        "msg_id": item.msg_id,
                                    },
                                    tooltip="移除",
                                    on_click=handle_context_click,
                                ),
                            ]
                        ),
                    ),
                ],
            )

            list_tile_list.append(col)
        return list_tile_list

    list_view = ft.ListView(spacing=10, padding=20, scroll="auto", controls=[])

    def create_main_card():
        """
        生成主视图
        """
        return ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            height=int(height * 0.8),
            content=list_view,
        )

    def create_bottom_card():
        """
        生成底部按钮
        """
        return ft.Container(
            height=50,
            align=ft.Alignment.CENTER,
            content=ft.Row(
                margin=ft.Margin(left=24),
                controls=[
                    ft.Button(
                        icon=ft.Icons.EDIT,
                        style=ft.ButtonStyle(
                            shape=ft.ContinuousRectangleBorder(radius=30),
                            bgcolor=ft.Colors.PINK_50,
                        ),
                        content="手动点歌",
                        on_click=handle_create_click,
                    ),
                    ft.Button(
                        icon=ft.Icons.DOWNLOAD,
                        style=ft.ButtonStyle(
                            shape=ft.ContinuousRectangleBorder(radius=30),
                            bgcolor=ft.Colors.PINK_50,
                        ),
                        content="导出列表",
                        on_click=handle_export_click,
                    ),
                    ft.Button(
                        icon=ft.Icons.DELETE,
                        style=ft.ButtonStyle(
                            shape=ft.ContinuousRectangleBorder(radius=30),
                            bgcolor=ft.Colors.PINK_50,
                        ),
                        content="清除列表",
                        on_click=on_clear,
                    ),
                ],
            ),
        )

    page.run_task(on_mount)

    return ft.View(
        route="/",
        controls=[create_main_card(), create_bottom_card()],
    )
