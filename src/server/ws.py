import time
import multiprocessing
from .app import app
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
from src.database import Db as conn
from src.bili import MyLive
from src.utils import logger
from bilibili_api import Credential


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
multiprocessing.set_start_method("spawn")


async def on_bili_danmu(event):
    await manager.broadcast(event)


async def create_bili_process(room_id: int):
    bili_credential = await conn.get_bcredential(enable=True)
    cred = Credential(
        sessdata=bili_credential.sessdata,
        bili_jct=bili_credential.bili_jct,
        buvid3=bili_credential.buvid3,
        buvid4=bili_credential.buvid4,
        dedeuserid=bili_credential.dedeuserid,
        ac_time_value=bili_credential.ac_time_value
    )
    instance = MyLive(room_id=room_id, credentials=cred)
    instance.on("danmu")(on_bili_danmu)
    task = multiprocessing.Process(target=instance.start, args=(), daemon=True, name=f"bili_{room_id}")
    task.start()
    return task


@app.websocket("/bili/{room_id}/ws")
async def ws_bili_endpoint(*, websocket: WebSocket, room_id: int):
    task = await create_bili_process(room_id)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "heartbeat":
                await manager.send_json({"data": int(time.time())}, websocket)
    except WebSocketException as ex:
        logger.exception(ex)
    except WebSocketDisconnect:
        task.kill()
        task.join()
        task.close()
        manager.disconnect(websocket)
