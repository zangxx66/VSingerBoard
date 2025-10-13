import json
from aiohttp import web
from typing import Any
from . import logger


class WebSocketServer:
    """
    一个简单的WebSocket服务器类，用于处理WebSocket连接和消息。
    该服务器可以被编程方式启动和停止。
    """

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.app.router.add_get("/", self.websocket_handler)
        self._clients = set()
        self.runner = None
        self.site = None

    async def websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """
        处理WebSocket连接请求
        :param request: aiohttp的Request对象
        :return: WebSocket响应
        """
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self._clients.add(ws)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    await self.on_message(ws, msg.data)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.warning(f"ws connection closed with exception {ws.exception()}")
        finally:
            self._clients.remove(ws)

        return ws

    async def on_message(self, ws: web.WebSocketResponse, message: str):
        """
        处理从客户端接收到的消息
        :param ws: WebSocket连接对象
        :param message: 接收到的消息字符串
        """
        # 默认实现：简单地将接收到的消息回显给客户端
        await ws.send_str(f"Echo: {message}")

    async def broadcast(self, message: Any):
        """
        广播消息给所有连接的客户端
        :param message: 要发送的消息，可以是字符串或字典
        """
        if isinstance(message, dict):
            message = json.dumps(message)

        for ws in self._clients:
            await ws.send_str(message)

    async def start(self):
        """
        启动WebSocket服务器。
        """
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        logger.info(f"WebSocket server has started at ws://{self.host}:{self.port}")

    async def stop(self):
        """
        停止WebSocket服务器。
        """
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("WebSocket server has stopped.")
