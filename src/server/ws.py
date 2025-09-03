import time
from .app import app
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
from src.database import Db as conn
from src.bili import MyLive
from src.utils import logger


class WsManager:
    def __init__(cls):
        cls.active_connections: list[WebSocket] = []

    async def connect(cls, ws: WebSocket):
        await ws.accept()
        cls.active_connections.append(ws)

    async def send_text(cls, msg: str, ws: WebSocket):
        await ws.send_text(msg)

    async def send_json(cls, msg: dict, ws: WebSocket):
        await ws.send_json(msg)

    async def broadcast(cls, msg: dict):
        for connection in cls.active_connections:
            await connection.send_json(msg)

    async def disconnect(cls, ws: WebSocket):
        cls.active_connections.remove(ws)


manager = WsManager()


async def on_danmu(event):
    await manager.broadcast(event)


@app.websocket("/bili/{room_id}/ws")
async def ws_endpoint(*, websocket: WebSocket, room_id: int):
    credential = await conn.get_bcredential(enable=True)
    instance = MyLive(room_id=room_id, credential=credential)
    instance.on("danmu")(on_danmu)
    instance.start()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "heartbeat":
                await manager.send_json({"data": int(time.time())}, websocket)
    except WebSocketException as ex:
        logger.exception(ex)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
