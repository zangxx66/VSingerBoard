import flet as ft
from flet import Ref
from src.utils import dyconfigItem, async_worker
from src.database import Db as db
from src.live import douyin_manager
from .progress import NProgress
from .toast import ModernToast


def douyin_container(page: ft.Page):

    id_text = Ref[ft.TextField]()
    room_id_text = Ref[ft.TextField]()
    sing_prefix_text = Ref[ft.TextField]()
    sing_cd_text = Ref[ft.TextField]()
    fans_lv_text = Ref[ft.TextField]()
    nprogress = NProgress(page)

    async def on_save_click(e: ft.Event[ft.Button]):
        """
        保存设置
        """
        data = dyconfigItem(
            id=int(id_text.current.value),
            room_id=int(room_id_text.current.value),
            sing_prefix=sing_prefix_text.current.value,
            sing_cd=int(sing_cd_text.current.value),
            fans_level=int(fans_lv_text.current.value)
        )
        result = await async_worker.run_db_operation(db.add_or_updae_dy_config(**data.__dict__))
        if result > 0:
            async_worker.submit(douyin_manager.restart())
            ModernToast.success(page, "保存成功")
        else:
            ModernToast.warning(page, "保存失败")

    def create_form():
        """
        创建表单
        """
        return ft.Card(
            content=ft.Row(
                wrap=True,
                controls=[
                    ft.TextField(label="id", ref=id_text, visible=False),
                    ft.TextField(label="房间号", ref=room_id_text, input_filter=ft.InputFilter(regex_string=r"^[1-9]\d*$")),
                    ft.TextField(label="点歌指令", ref=sing_prefix_text),
                    ft.TextField(label="点歌cd", ref=sing_cd_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.TextField(label="粉团等级", ref=fans_lv_text, input_filter=ft.InputFilter(regex_string=r"^\d+$")),
                    ft.Button(content="保存", style=ft.ButtonStyle(shape=ft.ContinuousRectangleBorder(radius=30), bgcolor=ft.Colors.PRIMARY_FIXED_DIM), on_click=on_save_click)
                ]
            )
        )

    async def on_mount():
        nprogress.start()
        data = await async_worker.run_db_operation(db.get_dy_config())
        if data:
            id_text.current.value = data.id
            room_id_text.current.value = data.room_id
            sing_prefix_text.current.value = data.sing_prefix
            sing_cd_text.current.value = data.sing_cd
            fans_lv_text.current.value = data.fans_level
            page.update()
        nprogress.stop()

    page.run_task(on_mount)

    return ft.Container(
        content=create_form()
    )
