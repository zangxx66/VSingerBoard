import base64
from fastapi import APIRouter, Query, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bilibili_api import Credential, user
from bilibili_api.login_v2 import QrCodeLogin, QrCodeLoginChannel
from src.database import Db
from src.utils import setup_autostart, ResponseItem, bconfigItem, dyconfigItem, globalfigItem
from . import ipc_instance


router = APIRouter(tags=["api"])
qr_code_login: QrCodeLogin


class BiliCredential(BaseModel):
    id: int
    enable: bool


@router.get("/get_bili_config", response_model=ResponseItem)
async def get_bili_config():
    config = await Db.get_bconfig()
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(config)})


@router.post("/add_or_update_bili_config", response_model=ResponseItem)
async def add_or_update_bili_config(data: bconfigItem = Body(..., embed=True)):
    result = await Db.add_or_update_bili_config(**data.__dict__)
    msg = "设置成功" if result > 0 else "设置失败"
    code = 0 if result > 0 else -1
    if result > 0 and ipc_instance.ipc_manager:
        ipc_instance.ipc_manager.send_message("bilibili_ws_reconnect")
    return JSONResponse(status_code=200, content={"code": code, "msg": msg, "data": result})


@router.get("/get_bili_credential_list", response_model=ResponseItem)
async def get_bili_credential_list():
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


@router.post("/update_bili_credential")
async def update_bili_credential(data: BiliCredential = Body(..., embed=True)):
    result = await Db.update_bcredential(pk=data.id, enable=data.enable)
    if result:
        ipc_instance.ipc_manager.send_message("bilibili_ws_reconnect")
        return ResponseItem(code=0, msg="设置成功", data=None)
    return ResponseItem(code=-1, msg="设置失败", data=None)


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
    qr_state = await qr_code_login.check_state()
    if qr_code_login.has_done():
        bili_cred = qr_code_login.get_credential()
        new_dic = bili_cred.__dict__
        model_fileds = ['ac_time_value', 'bili_jct', 'buvid3', 'buvid4', 'dedeuserid', 'enable', 'id', 'sessdata', 'uid']
        model_dic = {k: v for k, v in new_dic.items() if v is not None and k in model_fileds}
        uid = model_dic["dedeuserid"]
        model_dic["uid"] = uid
        model_dic["enable"] = False
        cred = await Db.get_bcredential(uid=uid)
        if not cred:
            await Db.add_bcredential(**model_dic)
        else:
            new_dic["enable"] = cred.enable
            await Db.update_bcredential(pk=cred.id, **model_dic)
        qr_code_login = None
        return ResponseItem(code=0, msg="success", data=None)
    return ResponseItem(code=0, msg="qr_state", data={"data": qr_state.value})


@router.get("/get_dy_config")
async def get_dy_config():
    result = await Db.get_dy_config()
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(result)})


@router.post("/add_or_update_dy_config", response_model=ResponseItem)
async def add_or_update_dy_config(data: dyconfigItem = Body(..., embed=True)):
    result = await Db.add_or_updae_dy_config(**data.__dict__)
    msg = "设置成功" if result > 0 else "设置失败"
    code = 0 if result > 0 else -1
    if result > 0 and ipc_instance.ipc_manager:
        ipc_instance.ipc_manager.send_message("douyin_ws_reconnect")
    return JSONResponse(status_code=200, content={"code": code, "msg": msg, "data": result})


@router.get("/get_global_config")
async def get_global_config():
    result = await Db.get_gloal_config()
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(result)})


@router.post("/add_or_update_global_config")
async def add_or_update_global_config(data: globalfigItem = Body(..., embed=True)):
    if data.startup is not None:
        startup_result = setup_autostart(data.startup)
        if not startup_result:
            return ResponseItem(code=-1, msg="开机启动更新失败", data=None)
    result = await Db.add_or_update_gloal_config(**data.__dict__)
    code = 0 if result > 0 else -1
    msg = "设置成功" if result > 0 else "设置失败"
    return JSONResponse(status_code=200, content={"code": code, "msg": msg, "data": result})
