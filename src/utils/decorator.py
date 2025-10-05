import asyncio
from typing import Callable, Coroutine, Union


class Decorator:
    """
    一个简单的事件装饰器类，用于注册和分发事件。
    它支持将同步函数和异步协程作为事件处理器。
    """
    __handlers__ = {}

    def add_listener(self, event: str, handler: Union[Callable, Coroutine]):
        """
        为指定事件添加一个监听器（处理器）。

        :param event: 事件的名称（字符串）。
        :param handler: 要添加的函数或协程处理器。
        """
        name = event.upper()
        if name not in self.__handlers__:
            self.__handlers__[name] = []
        self.__handlers__[name].append(handler)

    def remove_listener(self, name: str, handler: Union[Callable, Coroutine]):
        """
        从指定事件中移除一个特定的监听器。

        :param name: 事件的名称（字符串）。
        :param handler: 要移除的函数或协程处理器。
        :return: 如果成功移除，则返回True；否则返回False。
        """
        name = name.upper()
        if name in self.__handlers__:
            if handler in self.__handlers__[name]:
                self.__handlers__[name].remove(handler)
                return True
        return False

    def remove_all_listener(self):
        """
        移除所有事件的所有监听器。
        """
        self.__handlers__ = {}

    def on(self, event: str):
        """
        装饰器，用于将函数或协程添加为给定事件的监听器。

        :param event: 要监听的事件。

        :return: 一个装饰器，它将给定的函数或协程添加为给定事件的监听器。
        """

        def decorator(func: Union[Callable, Coroutine]):
            self.add_listener(event, func)
            return func

        return decorator

    def dispatch(self, event: str, *args, **kwargs):
        """
        分发一个事件，并调用所有注册的监听器。
        如果监听器是协程，则会创建asyncio任务来运行它们。

        :param event: 要分发的事件名称。
        :param args: 传递给监听器的位置参数。
        :param kwargs: 传递给监听器的关键字参数。
        """
        name = event.upper()
        if name in self.__handlers__:
            for callableorcoroutine in self.__handlers__[name]:
                obj = callableorcoroutine(*args, **kwargs)
                if isinstance(obj, Coroutine):
                    asyncio.create_task(obj)
