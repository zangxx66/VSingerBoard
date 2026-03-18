import asyncio
from typing import Callable, Dict, List


class EventEmitter:
    """
    一个简单的异步事件分发器，用于在不依赖特定框架的情况下处理组件间通信。
    """

    def __init__(self):
        # 存储事件名到回调函数列表的映射
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, callback: Callable):
        """
        订阅事件
        """
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
        return callback

    def off(self, event_name: str, callback: Callable):
        """
        取消订阅事件
        """
        if event_name in self._listeners:
            if callback in self._listeners[event_name]:
                self._listeners[event_name].remove(callback)

    async def emit(self, event_name: str, *args, **kwargs):
        """
        异步触发事件
        """
        if event_name in self._listeners:
            tasks = []
            for callback in self._listeners[event_name]:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(*args, **kwargs))
                else:
                    # 如果不是异步函数，直接在当前事件循环中调用
                    callback(*args, **kwargs)

            if tasks:
                await asyncio.gather(*tasks)

    def emit_sync(self, event_name: str, *args, **kwargs):
        """
        同步触发事件（仅适用于同步回调）
        """
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                if not asyncio.iscoroutinefunction(callback):
                    callback(*args, **kwargs)
                else:
                    # 警告或忽略：同步方法无法直接运行异步回调
                    pass
