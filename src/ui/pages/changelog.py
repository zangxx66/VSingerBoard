import flet as ft
from flet import Ref
from datetime import datetime as dt
from datetime import UTC
from src.utils import check_for_updates, async_worker
from ..components import NProgress


def main(page: ft.Page):
    url_launcher = ft.UrlLauncher()

    version_text = Ref[ft.Text]()
    published_text = Ref[ft.Text]()
    body_text = Ref[ft.Markdown]()

    async def on_mount():
        NProgress.start(page)
        version_info = await async_worker.run_db_operation(check_for_updates())

        if len(version_info["published_at"]) > 0:
            utc_str = version_info["published_at"]
            d = dt.fromisoformat(utc_str).replace(tzinfo=UTC).astimezone()
            version_info["published_at"] = d.strftime("%Y-%m-%d %H:%M:%S")
            published_text.current.value = version_info["published_at"]
        version_text.current.value = version_info["version"]
        body_text.current.value = version_info["body"]
        NProgress.stop(page)
        page.update()

    async def handle_link_click(e: ft.Event[ft.Markdown]):
        await url_launcher.launch_url(e.data)

    page.run_task(on_mount)

    return ft.View(
        route="/changelog",
        controls=[
            ft.Card(
                margin=ft.Margin.only(left=10, right=10),
                content=ft.ListView(
                    padding=ft.Padding.all(24),
                    spacing=8,
                    controls=[
                        ft.Text(size=28, ref=version_text),
                        ft.Text(size=18, ref=published_text),
                        ft.Markdown(
                            code_theme=ft.MarkdownCodeTheme.GITHUB,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            ref=body_text,
                            on_tap_link=handle_link_click
                        )
                    ]
                )
            ),
        ],
    )
