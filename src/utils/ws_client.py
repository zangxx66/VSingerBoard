import asyncio
import aiohttp
from typing import Optional
from .log import logger


class WebSocketClient:
    """
    一个基础的WebSocket客户端，用于连接指定的WebSocket服务器，并接收消息。

    支持自动重连机制。
    """

    def __init__(self, ssl: bool = True):
        """
        初始化WebSocket客户端。

        :param ssl: 是否启用SSL验证。
        """
        self.url = ""
        self.headers = {}
        self.max_retries = 5
        self.retry_delay = 5
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._is_running = False
        self._retry_count = 0
        self._reconnect_task: Optional[asyncio.Task] = None
        self._listen_task: Optional[asyncio.Task] = None
        self.status_code = 0  # 0:未连接, 1:已连接, 2:已断开, 3:连接失败
        self._ssl = ssl

    @property
    def is_connected(self):
        """
        获取真实的WebSocket布尔连接状态。

        :return: bool, True表示已连接，False表示未连接。
        """
        return self.ws is not None and not self.ws.closed

    async def connect(self):
        """
        连接到WebSocket服务器。
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)

        try:
            self.ws = await self.session.ws_connect(self.url, ssl=self._ssl, autoclose=False, heartbeat=5)
            logger.info(f"成功连接到 {self.url}")
            self._is_running = True
            self.status_code = 1  # 已连接
            self._retry_count = 0  # 重置重连计数器
            if self._reconnect_task:
                self._reconnect_task.cancel()
            self._listen_task = asyncio.create_task(self.listen())
        except aiohttp.ClientError as e:
            logger.error(f"连接失败: {e}")
            await self._schedule_reconnect()

    async def listen(self):
        """
        持续监听来自WebSocket服务器的消息。
        """
        if not self.ws:
            return

        try:
            while self._is_running:
                msg = await self.ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.on_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    await self.on_message(msg.data)
                elif msg.type in [aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR]:
                    if msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"WebSocket 错误: {self.ws.exception()}")
                    else:
                        logger.info("WebSocket 连接已关闭")
                    break
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")
        finally:
            if self._is_running:  # 如果是意外断开
                await self._schedule_reconnect()

    async def on_message(self, message):
        """
        处理从服务器收到的消息。子类应重写此方法。

        :param message: 从服务器收到的消息。
        """
        raise NotImplementedError("子类必须实现 on_message 方法")

    async def send(self, data):
        """
        向WebSocket服务器发送消息。

        :param data: 要发送的数据。
        """
        if self.is_connected:
            if isinstance(data, bytes):
                await self.ws.send_bytes(data)
            else:
                await self.ws.send_str(str(data))
        else:
            logger.warning("WebSocket未连接，无法发送消息。")

    async def _schedule_reconnect(self):
        """
        安排重连任务。
        """
        if self._is_running and self._retry_count < self.max_retries:
            self._retry_count += 1
            self.status_code = 2
            logger.info(f"将在 {self.retry_delay} 秒后尝试重新连接 (第 {self._retry_count}/{self.max_retries} 次)")
            self._reconnect_task = asyncio.create_task(self._reconnect())
        else:
            if self._is_running:
                logger.error("已达到最大重连次数，将关闭客户端。")
                self.status_code = 3  # 连接失败
                await self.close()

    async def _reconnect(self):
        """
        执行重连操作。
        """
        if self._listen_task:
            self._listen_task.cancel()
        if self.ws:
            await self.ws.close()
        self.ws = None
        await asyncio.sleep(self.retry_delay)
        await self.connect()

    async def close(self):
        """
        关闭WebSocket连接和客户端会话。
        """
        if self._is_running and self.status_code != 3:
            self.status_code = 2  # 已断开
        self._is_running = False

        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
        if self.ws and not self.ws.closed:
            await self.ws.close()
            logger.info("WebSocket连接已成功关闭")
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("客户端会话已成功关闭")
        self.ws = None
        self.session = None

    async def start(self):
        """
        启动客户端并开始连接。
        """
        if not self._is_running:
            self.status_code = 0  # 重置状态
            await self.connect()
