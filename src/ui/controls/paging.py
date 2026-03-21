import inspect
import flet as ft
from typing import Optional
from flet import control, Card, ControlEventHandler, Ref


@control
class Pagination(Card):
    """
    Pagination 分页器
    """

    total: int = 0
    """
    总条目数
    """

    size: int = 10
    """
    分页大小
    """

    on_page_change: Optional[ControlEventHandler["Pagination"]] = None
    """
    翻页时触发
    """

    def init(self):
        self._page = 1
        self._page_num = (self.total + self.size - 1) // self.size
        self._ref_page = Ref[ft.Text]()
        self.content = ft.Row(
            margin=ft.Margin.only(left=24),
            controls=[
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_LEFT,
                    on_click=self._goto_first_page,
                    tooltip="首页"
                ),
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD_ARROW_LEFT,
                    on_click=self._prev_page,
                    tooltip="上一页",
                ),
                ft.Text(value=self._page, ref=self._ref_page),
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD_ARROW_RIGHT,
                    on_click=self._next_page,
                    tooltip="下一页",
                ),
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                    on_click=self._goto_last_page,
                    tooltip="尾页",
                )
            ]
        )

    def before_update(self):
        self._page_num = (self.total + self.size - 1) // self.size
        self._ref_page.current.value = self._page
        return super().before_update()

    async def _set_page(self, p=None, delta=0):
        if self.on_page_change is None:
            return
        if p is not None:
            self._page = p
        elif delta:
            self._page += delta
        else:
            return
        self.data = self._page
        if inspect.iscoroutinefunction(self.on_page_change):
            await self.on_page_change(ft.Event[self](name="Pagination", control=self))
        else:
            self.on_page_change(ft.Event[self](name="Pagination", control=self))
        self.update()

    async def _next_page(self, e):
        if self._page < self._page_num:
            await self._set_page(delta=1)

    async def _prev_page(self, e):
        if self._page > 1:
            await self._set_page(delta=-1)

    async def _goto_first_page(self, e):
        if self._page > 1:
            await self._set_page(p=1)

    async def _goto_last_page(self, e):
        if self._page != self._page_num:
            await self._set_page(p=self._page_num)
