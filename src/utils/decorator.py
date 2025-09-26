import asyncio
from typing import Callable, Coroutine, Union


class Decorator:
    __handlers__ = {}

    def add_listener(self, event: str, handler: Union[Callable, Coroutine]):
        name = event.upper()
        if name not in self.__handlers__:
            self.__handlers__[name] = []
        self.__handlers__[name].append(handler)

    def remove_listener(self, name: str, handler: Union[Callable, Coroutine]):
        name = name.upper()
        if name in self.__handlers__:
            if handler in self.__handlers__[name]:
                self.__handlers__[name].remove(handler)
                return True
        return False

    def remove_all_listener(self):
        self.__handlers__ = {}

    def on(self, event: str):
        """
        Decorator to add a function or coroutine as a listener for the given event.

        Args:
            event (str): The event to listen for.

        Returns:
            Callable[[Union[Callable, Coroutine]], Union[Callable, Coroutine]]: A decorator which adds the given function or coroutine as a listener for the given event.
        """

        def decorator(func: Union[Callable, Coroutine]):
            self.add_listener(event, func)
            return func

        return decorator

    def dispatch(self, event: str, *args, **kwargs):
        name = event.upper()
        if name in self.__handlers__:
            for callableorcoroutine in self.__handlers__[name]:
                obj = callableorcoroutine(*args, **kwargs)
                if isinstance(obj, Coroutine):
                    asyncio.create_task(obj)
