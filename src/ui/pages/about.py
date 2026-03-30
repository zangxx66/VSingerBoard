import flet as ft
from flet import Ref
from src.utils import resource_path, async_worker, check_for_updates, __version__ as version
from ..controls import ModernToast


def main(page: ft.Page):
    url_launcher = ft.UrlLauncher()
    update_btn = Ref[ft.Button]()

    async def handle_click(e: ft.Event[ft.Button]):
        if e.control.data == "feedback":
            await url_launcher.launch_url(
                "https://github.com/zangxx66/VSingerBoard/issues"
            )
        elif e.control.data == "github":
            await url_launcher.launch_url("https://github.com/zangxx66/VSingerBoard")
        elif e.control.data == "update":
            update_btn.current.icon = ft.Icons.LOCAL_DINING
            update_btn.current.disabled = True
            update_btn.current.update()
            version_info = await async_worker.run_db_operation(check_for_updates())
            if version_info["code"] == -1:
                ModernToast.warning(page, version_info["msg"])
            else:
                ModernToast.info(page, version_info["msg"])
            update_btn.current.icon = ft.Icons.CHECK
            update_btn.current.disabled = False
            update_btn.current.update()
        else:
            await url_launcher.launch_url("https://space.bilibili.com/909267")

    logo = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Image(src=resource_path("icons/logo.png"), width=128, height=128)
        ]
    )

    title = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Text(value="点歌姬", size=20)
        ]
    )

    ver = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Text(value=f"v{version}"),
            ft.Button(
                icon=ft.Icons.CHECK,
                content="检查更新",
                data="update",
                bgcolor=ft.Colors.PRIMARY_FIXED_DIM,
                color=ft.Colors.WHITE,
                ref=update_btn,
                on_click=handle_click,
            ),
        ],
    )

    actions = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Button(
                icon=ft.Icons.CODE,
                content="GitHub仓库",
                data="github",
                bgcolor=ft.Colors.GREY_400,
                color=ft.Colors.WHITE,
                on_click=handle_click,
            ),
            ft.Button(
                icon=ft.Icons.HOME_FILLED,
                content="作者主页",
                data="bilibili",
                bgcolor=ft.Colors.PINK_ACCENT_200,
                color=ft.Colors.WHITE,
                on_click=handle_click,
            ),
            ft.Button(
                icon=ft.Icons.FEEDBACK,
                content="问题反馈",
                data="feedback",
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                on_click=handle_click,
            ),
        ],
    )

    main_container = ft.Card(
        margin=ft.Margin.only(left=10, right=10),
        height=page.height,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                logo,
                title,
                ver,
                actions
            ]
        )
    )

    return ft.View(
        route="/about",
        controls=[main_container],
    )
