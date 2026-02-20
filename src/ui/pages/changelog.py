import flet as ft
from flet import AppBar, NavigationDrawer
from datetime import datetime as dt
from datetime import UTC
from src.utils import check_for_updates, async_worker


def main(page: ft.Page, appbar: AppBar, drawer: NavigationDrawer):

    version_info = async_worker.run_sync(check_for_updates())

    if version_info["published_at"] is not None:
        utc_str = version_info["published_at"]
        d = dt.fromisoformat(utc_str).replace(tzinfo=UTC).astimezone()
        version_info["published_at"] = d.strftime("%Y-%m-%d %H:%M:%S")

    return ft.View(
        route="/changelog",
        controls=[
            ft.Card(
                content=ft.ListView(
                    padding=ft.Padding.all(24),
                    spacing=8,
                    controls=[
                        ft.Text(size=28, value=version_info["version"]),
                        ft.Text(size=18, value=version_info["published_at"]),
                        ft.Markdown(
                            value=version_info["body"]
                        )
                    ]
                )
            ),
        ],
        appbar=appbar,
        drawer=drawer
    )
