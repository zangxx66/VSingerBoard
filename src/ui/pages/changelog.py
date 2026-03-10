import flet as ft
from flet import AppBar, NavigationDrawer, Ref
from datetime import datetime as dt
from datetime import UTC
from src.utils import check_for_updates, async_worker
from src.ui.components.progress import NProgress


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):

    version_text = Ref[ft.Text]()
    published_text = Ref[ft.Text]()
    body_text = Ref[ft.Markdown]()
    nprogress = NProgress(page)

    async def on_mount():
        nprogress.start()
        version_info = await async_worker.run_db_operation(check_for_updates())

        if version_info["published_at"] is not None:
            utc_str = version_info["published_at"]
            d = dt.fromisoformat(utc_str).replace(tzinfo=UTC).astimezone()
            version_info["published_at"] = d.strftime("%Y-%m-%d %H:%M:%S")
            published_text.current.value = version_info["published_at"]
        version_text.current.value = version_info["version"]
        body_text.current.value = version_info["body"]
        nprogress.stop()
        page.update()

    page.run_task(on_mount)

    return ft.View(
        route="/changelog",
        controls=[
            ft.Card(
                content=ft.ListView(
                    padding=ft.Padding.all(24),
                    spacing=8,
                    controls=[
                        ft.Text(size=28, ref=version_text),
                        ft.Text(size=18, ref=published_text),
                        ft.Markdown(
                            ref=body_text
                        )
                    ]
                )
            ),
        ],
        appbar=appbar,
        drawer=drawer
    )
