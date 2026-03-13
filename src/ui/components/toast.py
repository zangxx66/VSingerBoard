import flet as ft
import asyncio


class ModernToast:
    """
    一个类似前端样式的 Toast 组件。
    支持多种类型、位置自定义、显示时长自定义、图标显示以及进度条。
    """

    _view_containers: dict[int, dict[str, ft.Column]] = {}

    @staticmethod
    def _get_type_config(toast_type: str):
        """获取预设类型的颜色和默认图标"""
        configs: dict[str, dict[str, str | ft.IconData]] = {
            "info": {
                "color": ft.Colors.BLUE_400,
                "icon": ft.Icons.INFO_OUTLINE,
            },
            "success": {
                "color": ft.Colors.GREEN_400,
                "icon": ft.Icons.CHECK_CIRCLE_OUTLINE,
            },
            "warning": {
                "color": ft.Colors.ORANGE_400,
                "icon": ft.Icons.WARNING_AMBER_ROUNDED,
            },
            "error": {
                "color": ft.Colors.RED_400,
                "icon": ft.Icons.ERROR_OUTLINE_ROUNDED,
            },
        }
        return configs.get(toast_type, configs["info"])

    @staticmethod
    def _set_column_position(column: ft.Column, position: str):
        column.top = column.bottom = column.left = column.right = None

        if "top" in position:
            column.top = 20
        elif "bottom" in position:
            column.bottom = 20
        else:
            column.top = 50

        if "left" in position:
            column.left = 20
            column.horizontal_alignment = ft.CrossAxisAlignment.START
        elif "right" in position:
            column.right = 20
            column.horizontal_alignment = ft.CrossAxisAlignment.END
        else:
            column.left = 0
            column.right = 0
            column.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    @staticmethod
    async def _get_or_create_stack(page: ft.Page, position: str):
        """
        在当前激活的 View 中寻找或创建 Stack 容器。
        """
        if not page.views:
            return None

        current_view = page.views[-1]
        view_key = id(current_view)

        if view_key not in ModernToast._view_containers:
            ModernToast._view_containers[view_key] = {}

        if position not in ModernToast._view_containers[view_key]:
            stack_column = ft.Column(
                tight=True,
                spacing=10,
            )
            ModernToast._set_column_position(stack_column, position)

            if not current_view.controls or not (isinstance(current_view.controls[0], ft.Stack) and hasattr(current_view.controls[0], "_is_toast_wrapper")):
                original_controls = ft.Column(current_view.controls[:], expand=True)
                main_stack = ft.Stack(
                    controls=[
                        original_controls, stack_column
                    ],
                    expand=True
                )
                current_view.controls.clear()
                current_view.controls.append(main_stack)
            else:
                current_view.controls[-1].controls.append(stack_column)

            ModernToast._view_containers[view_key][position] = stack_column
            page.update()

        return ModernToast._view_containers[view_key][position]

    @staticmethod
    async def _show_async(
        page: ft.Page,
        message: str,
        type: str = "info",
        position: str = "top_center",
        duration: int = 1500,
        icon: str = None,
        progress: bool = True
    ):
        if duration < 100:
            duration = int(duration * 1000)

        config = ModernToast._get_type_config(type)
        bg_color = config["color"]

        stack_column = await ModernToast._get_or_create_stack(page, position)
        if not stack_column:
            return

        progress_bar = None
        if progress:
            progress_bar = ft.ProgressBar(
                value=0,
                color=ft.Colors.PRIMARY_FIXED_DIM,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                height=2,
            )

        content_row = ft.Row(
            controls=[
                ft.Icon(icon, color=ft.Colors.WHITE, size=20) if icon else ft.Container(),
                ft.Text(message, color=ft.Colors.WHITE, weight=ft.FontWeight.W_400, size=14),
            ],
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        toast_card = ft.Container(
            content=ft.Column(
                controls=[
                    content_row,
                    ft.Container(
                        content=progress_bar,
                        margin=ft.Margin.only(top=5)
                    ) if progress_bar else ft.Container(),
                ],
                tight=True,
                spacing=0,
            ),
            bgcolor=bg_color,
            padding=ft.Padding.symmetric(vertical=10, horizontal=16),
            border_radius=ft.BorderRadius.all(8),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            ),
            animate_opacity=300,
            opacity=0,
            offset=ft.Offset(0, -0.2) if "top" in position else ft.Offset(0, 0.2),
            animate_offset=300,
            width=200,
        )

        stack_column.controls.append(toast_card)
        page.update()

        toast_card.opacity = 1
        toast_card.offset = ft.Offset(0, 0)
        page.update()

        if progress and duration > 0:
            steps = 40
            sleep_interval = duration / steps / 1000
            for i in range(steps):
                await asyncio.sleep(sleep_interval)
                progress_bar.value = (i + 1) / steps
                page.update()
        else:
            await asyncio.sleep(duration / 1000)

        toast_card.opacity = 0
        toast_card.offset = ft.Offset(0, -0.2) if "top" in position else ft.Offset(0, 0.2)
        page.update()
        await asyncio.sleep(0.3)

        if toast_card in stack_column.controls:
            stack_column.controls.remove(toast_card)
            page.update()

    @staticmethod
    def show(page: ft.Page, message: str, **kwargs):
        if hasattr(page, "run_task"):
            page.run_task(ModernToast._show_async, page, message, **kwargs)
        else:
            asyncio.create_task(ModernToast._show_async(page, message, **kwargs))

    @staticmethod
    def success(page: ft.Page, message: str, icon=ft.Icons.CHECK_CIRCLE_OUTLINE, **kwargs):
        ModernToast.show(page, message, type="success", icon=icon, **kwargs)

    @staticmethod
    def info(page: ft.Page, message: str, icon=ft.Icons.INFO_OUTLINE, **kwargs):
        ModernToast.show(page, message, type="info", icon=icon, **kwargs)

    @staticmethod
    def warning(page: ft.Page, message: str, icon=ft.Icons.WARNING_AMBER_ROUNDED, **kwargs):
        ModernToast.show(page, message, type="warning", icon=icon, **kwargs)

    @staticmethod
    def error(page: ft.Page, message: str, icon=ft.Icons.ERROR_OUTLINE_ROUNDED, **kwargs):
        ModernToast.show(page, message, type="error", icon=icon, **kwargs)
