import flet as ft
import asyncio


class NProgress:
    _active_progresses = {}

    @staticmethod
    def start(page: ft.Page):
        # 如果已经存在进度条，则不重复创建
        if page in NProgress._active_progresses:
            return

        progress_overlay = ft.Stack(
            controls=[
                ft.Container(
                    expand=True,
                    margin=ft.Margin.only(top=50),
                    height=page.window.height - 50,
                    bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                    blur=50,
                ),
                ft.Column(
                    controls=[ft.ProgressRing()],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    align=ft.Alignment.CENTER
                ),
            ],
            opacity=0,  # 初始透明度为 0
            animate_opacity=300,  # 动画时间 300ms
        )

        NProgress._active_progresses[page] = progress_overlay
        page.overlay.append(progress_overlay)
        page.update()

        # 触发淡入动画
        progress_overlay.opacity = 1
        page.update()

    @staticmethod
    def stop(page: ft.Page):
        # 移除对应的进度条并更新页面
        if page in NProgress._active_progresses:
            progress_overlay = NProgress._active_progresses.pop(page)

            async def animate_stop():
                # 触发淡出动画
                progress_overlay.opacity = 0
                page.update()
                # 等待动画完成（300ms）后移除
                await asyncio.sleep(0.3)
                if progress_overlay in page.overlay:
                    page.overlay.remove(progress_overlay)
                page.update()

            # 使用异步任务执行动画和移除操作
            if hasattr(page, "run_task"):
                page.run_task(animate_stop)
            else:
                asyncio.create_task(animate_stop())
