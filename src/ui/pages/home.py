import time
import io
import pyautogui
import asyncio
import pandas as pd
import flet as ft
from flet import Page, AppBar, NavigationDrawer
from src.utils import DanmuInfo, logger, timespan_to_localtime
from ..components.toast import ModernToast


def main(page: Page, appbar: AppBar, drawer: NavigationDrawer):
    _, height = pyautogui.size()
    list_tile_list: list[ft.Column] = []
    danmaku_list: list[DanmuInfo] = []

    def on_message(_, msg):
        """
        更新点歌列表
        """
        nonlocal danmaku_list
        danmaku_list = msg
        list_view.controls = generate_list()
        page.update()

    page.pubsub.subscribe_topic("add", on_message)

    async def handle_context_click(e: ft.Event[ft.PopupMenuItem]):
        """
        ContextMenu 事件
        """
        if e.control.content == "复制":
            await on_copy(e.control.data)
        if e.control.content == "移除":
            page.pubsub.send_all_on_topic("del", {"source": e.control.data["source"], "msg_id": e.control.data["msg_id"]})
            ModernToast.success(page, "已移除")

    async def on_copy(e: ft.Event[ft.ListTile]):
        """
        复制歌名到剪切板
        """
        await ft.Clipboard().set(e.control.data)
        ModernToast.success(page, "已复制")

    def on_clear(e: ft.Event[ft.Button]):
        """
        清除列表
        """
        if len(danmaku_list) == 0:
            ModernToast.info(page, "没有数据")
            return
        page.pubsub.send_all_on_topic("clear", None)
        danmaku_list.clear()
        page.update()
        ModernToast.success(page, "清除列表成功")

    async def handle_export_click(e: ft.Event[ft.Button]):
        """
        导出列表
        """
        try:
            if len(danmaku_list) == 0:
                ModernToast.info(page, "没有数据")
                return
            df_dict = {
                "日期": [timespan_to_localtime(item["send_time"]) for item in danmaku_list],
                "昵称": [item["uname"] for item in danmaku_list],
                "歌名": [item["msg"] for item in danmaku_list],
                "平台": [item["source"] for item in danmaku_list]
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
                src_bytes=excel_bytes
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
            page.pubsub.send_all_on_topic("manual", {"source": source.value, "data": DanmuInfo(
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
                source=source.value
            )})
            page.pop_dialog()

        page.show_dialog(ft.AlertDialog(
            title="手动点歌",
            content=ft.Column(
                height=240,
                controls=[
                    uname := ft.TextField(
                        label="用户昵称"
                    ),
                    msg := ft.TextField(
                        label="点歌内容"
                    ),
                    source := ft.Dropdown(label="点歌平台", value="bilibili", options=[
                        ft.DropdownOption(key="bilibili", content=ft.Text("哔哩哔哩")),
                        ft.DropdownOption(key="douyin", content=ft.Text("抖音"))
                    ])
                ]
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda ee: page.pop_dialog()),
                ft.TextButton("提交", on_click=submit)
            ]
        ))

    def create_menu(data):
        """
        创建 ContextMenu 菜单
        """
        menu = ft.ContextMenu(
            content=ft.IconButton(ft.Icons.MORE_VERT, on_click=lambda e: asyncio.create_task(menu.open())),
            items=[
                ft.PopupMenuItem(
                    content="复制",
                    data=data["subtitle"],
                    on_click=handle_context_click
                ),
                ft.PopupMenuItem(
                    content="移除",
                    data=data,
                    on_click=handle_context_click
                )
            ]
        )
        return menu

    def generate_list():
        """
        生成列表
        """
        nonlocal list_tile_list
        list_tile_list.clear()
        for item in danmaku_list:
            col = ft.Column(
                data={"title": item["uname"], "subtitle": item["msg"]},
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE),
                        bgcolor=ft.Colors.BLUE_ACCENT_200,
                        title=item["uname"],
                        subtitle=item["msg"],
                        trailing=create_menu({"title": item["uname"], "subtitle": item["msg"], "source": item["source"], "msg_id": item["msg_id"]}),
                        data=item["msg"],
                        mouse_cursor=ft.MouseCursor.CLICK,
                        on_click=on_copy
                    ),
                ]
            )

            list_tile_list.append(col)
        return list_tile_list

    list_view = ft.ListView(
        spacing=10,
        padding=20,
        scroll="auto",
        controls=[]
    )

    def create_main_card():
        """
        生成主视图
        """
        return ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            height=int(height * .75),
            content=list_view
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
                    ft.Button(icon=ft.Icons.EDIT, style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PINK_50), content="手动点歌", on_click=handle_create_click),
                    ft.Button(icon=ft.Icons.DOWNLOAD, style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PINK_50), content="导出列表", on_click=handle_export_click),
                    ft.Button(icon=ft.Icons.DELETE, style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PINK_50), content="清除列表", on_click=on_clear)
                ]
            )
        )

    return ft.View(
        route="/",
        controls=[
            create_main_card(),
            create_bottom_card()
        ],
        appbar=appbar,
        drawer=drawer,
    )
