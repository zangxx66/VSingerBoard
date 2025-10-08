import logging
from multiprocessing import Queue
from queue import Empty
from typing import Any

# 暴露 Empty 异常，方便外部模块捕获
MessageQueueEmpty = Empty
logger = logging.getLogger("danmaku")


class IPCManager:
    """
    负责管理和操作多进程通信（IPC）队列的类。
    """
    def __init__(self, queue: Queue = None):
        """
        构造函数。如果提供了队列，则使用现有队列，否则创建新队列。
        """
        if queue is not None:
            self._message_queue = queue
        else:
            self._message_queue: Queue = Queue()
        logger.info("IPCManager initialized.")

    @property
    def message_queue(self):
        """
        获取内部的多进程队列实例。
        """
        return self._message_queue

    @property
    def is_empty(self):
        """
        检查队列是否为空。
        """
        return self._message_queue.empty()

    def send_message(self, data: Any):
        """
        向队列中发送数据（阻塞）。
        """
        # 使用类内部的队列实例
        self._message_queue.put(data)

    def receive_message_nonblocking(self):
        """
        从队列中接收数据（非阻塞）。

        Raises:
            MessageQueueEmpty: 如果队列为空，立即抛出此异常。

        Returns:
            Any: 队列中的数据。
        """
        # 使用 get_nowait() 实现非阻塞
        return self._message_queue.get_nowait()

    def receive_message_blocking(self):
        """
        从队列中接收数据（阻塞）。

        在需要强制等待的场景下使用
        """
        return self._message_queue.get()

    def close(self):
        """
        关闭队列，释放相关资源。
        """
        try:
            # 1. 关闭队列的底层管道连接
            self._message_queue.close()
            logger.info("IPCManager queue closed.")

            # 2. 等待队列的内部管理线程退出
            self._message_queue.join_thread()
            logger.info("IPCManager queue thread joined.")

        except AttributeError:
            # 如果队列未初始化或已关闭，忽略错误
            pass
        except Exception as e:
            logger.error(f"Error closing IPCManager queue: {e}")
        logger.info("IPCManager queue closed.")
