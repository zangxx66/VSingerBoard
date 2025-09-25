import webview
import base64
import asyncio
from pydantic import BaseModel
from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, Body, Header, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from bilibili_api import Credential, user
from bilibili_api.login_v2 import QrCodeLogin, QrCodeLoginChannel
from src.database import Db
from src.jsBridge import restart_bili, restart_dy
from src.utils import setup_autostart

# Lock to serialize access to the bilibili-api library to prevent concurrency issues.
bilibili_api_lock = asyncio.Lock()


def verify_token(x_token: str = Header()):
    if x_token != webview.token:
        raise HTTPException("Authentication error")


router = APIRouter(tags=["api"], dependencies=[Depends(verify_token)])
qr_code_login: QrCodeLogin


class ResponseItem(BaseModel):
    code: int
    msg: Optional[str]
    data: Optional[Dict[str, Any]]


class subItem(BaseModel):
    id: int
    room_id: int
    source: str


class bconfigItem(BaseModel):
    id: int
    room_id: int
    modal_level: int
    user_level: int
    sing_prefix: str
    sing_cd: int


class dyconfigItem(BaseModel):
    id: int
    room_id: int
    sing_prefix: str
    sing_cd: int


class globalfigItem(BaseModel):
    id: int
    dark_mode: bool
    check_update: bool
    startup: bool


@router.get("/get_bili_config", response_model=ResponseItem)
async def get_bili_config():
    config = await Db.get_bconfig()
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(config)})


@router.post("/add_or_update_bili_config", response_model=ResponseItem)
async def add_or_update_bili_config(background_tasks: BackgroundTasks, data: bconfigItem = Body(..., embed=True)):
    data_dic = data.__dict__
    new_dic = {k: v for k, v in data_dic.items() if v is not None and k != "id"}
    msg = ""
    if data.id > 0:
        result = await Db.update_bconfig(pk=data.id, **new_dic)
        msg = "更新成功" if result else "更新失败"
    else:
        result = await Db.add_bconfig(**new_dic)
        msg = "添加成功" if result else "添加失败"
    if result:
        background_tasks.add_task(func=restart_bili)
    code = 0 if result else -1
    return ResponseItem(code=code, msg=msg, data=None)


@router.get("/get_bili_credential_list", response_model=ResponseItem)
async def get_bili_credential_list():
    async with bilibili_api_lock:
        query_list = await Db.get_bcredential_list()
        result = []
        for item in query_list:
            cred = Credential(
                sessdata=item.sessdata,
                bili_jct=item.bili_jct,
                buvid3=item.buvid3,
                buvid4=item.buvid4,
                dedeuserid=item.dedeuserid,
                ac_time_value=item.ac_time_value
            )
            up = user.User(uid=item.uid, credential=cred)
            up_info = await up.get_user_info()
            result.append({
                "id": item.id,
                "uname": up_info["name"],
                "avatar": up_info["face"],
                "uid": item.uid,
                "enable": item.enable
            })
        return ResponseItem(code=0, msg=None, data={"rows": jsonable_encoder(result)})


@router.get("/refresh_bili_credential", response_model=ResponseItem)
async def refresh_bili_credential(id: int = Query(...)):
    result = await Db.get_bcredential(pk=id)
    if not result:
        return ResponseItem(code=-1, msg="id不存在", data=None)
    cred = Credential(
        sessdata=result.sessdata,
        bili_jct=result.bili_jct,
        buvid3=result.buvid3,
        buvid4=result.buvid4,
        dedeuserid=result.dedeuserid,
        ac_time_value=result.ac_time_value
    )
    if await cred.check_valid():
        if await cred.check_refresh():
            await cred.refresh()
            data_dic = result.__dict__
            new_dic = {k: v for k, v in data_dic.items() if v is not None and k != "id"}
            await Db.update_bcredential(pk=result.id, **new_dic)
        return ResponseItem(code=0, msg="刷新成功", data=None)
    return ResponseItem(code=-1, msg="fail", data=None)


@router.post("/delete_bili_credential", response_model=ResponseItem)
async def delete_bili_credential(id: int = Body(..., embed=True)):
    result = await Db.delete_bcredential(pk=id)
    if result:
        return ResponseItem(code=0, msg="删除成功", data=None)
    else:
        return ResponseItem(code=-1, msg="删除失败", data=None)


@router.get("/get_bili_credential_code")
async def get_bili_credential_code():
    global qr_code_login
    qr_code_login = QrCodeLogin(platform=QrCodeLoginChannel.WEB)
    await qr_code_login.generate_qrcode()
    qr_code = qr_code_login.get_qrcode_picture()
    binary_data = qr_code.content
    encoded_string = base64.b64encode(binary_data).decode("utf-8")
    return ResponseItem(code=0, msg="", data={"data": f"data:image/png;base64,{encoded_string}"})


@router.get("/check_qr_code")
async def check_qr_code():
    global qr_code_login
    if qr_code_login.has_done():
        bili_cred = qr_code_login.get_credential()
        new_dic = bili_cred.__dict__
        uid = new_dic["dedeuserid"]
        new_dic["uid"] = uid
        new_dic["enable"] = False
        cred = await Db.get_bcredential(uid=uid)
        if not cred:
            await Db.add_bcredential(new_dic)
        else:
            new_dic["enable"] = cred.enable
            await Db.update_bcredential(pk=cred.id, **new_dic)
        return ResponseItem(code=0, msg="success", data=None)
    qr_state = await qr_code_login.check_state()
    return ResponseItem(code=0, msg="qr_state", data={"data": qr_state.value})


@router.get("/get_dy_config")
async def get_dy_config():
    result = await Db.get_dy_config()
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(result)})


@router.post("/add_or_update_dy_config", response_model=ResponseItem)
async def add_or_update_dy_config(background_tasks: BackgroundTasks, data: dyconfigItem = Body(..., embed=True)):
    data_dic = data.__dict__
    new_dic = {k: v for k, v in data_dic.items() if v is not None and k != "id"}
    msg = ""
    if data.id > 0:
        result = await Db.update_dy_config(pk=data.id, **new_dic)
        msg = "更新成功" if result else "更新失败"
    else:
        result = await Db.add_dy_config(**new_dic)
        msg = "添加成功" if result else "添加失败"
    if result:
        background_tasks.add_task(func=restart_dy)
    code = 0 if result else -1
    return ResponseItem(code=code, msg=msg, data=None)


@router.get("/get_global_config")
async def get_global_config():
    async with bilibili_api_lock:
        result = await Db.get_gloal_config()
        return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(result)})


@router.post("/add_or_update_global_config")
async def add_or_update_global_config(background_tasks: BackgroundTasks, data: globalfigItem = Body(..., embed=True)):
    data_dic = data.__dict__
    new_dic = {k: v for k, v in data_dic.items() if v is not None and k != "id"}
    msg = ""
    startup_result = setup_autostart(data.startup)
    if not startup_result:
        return ResponseItem(code=-1, msg="开机启动更新失败", data=None)
    if data.id > 0:
        result = await Db.update_gloal_config(pk=data.id, **new_dic)
        msg = "更新成功" if result else "更新失败"
    else:
        result = await Db.add_gloal_config(**new_dic)
        msg = "添加成功" if result else "添加失败"
    code = 0 if result else -1
    return ResponseItem(code=code, msg=msg, data=None)
