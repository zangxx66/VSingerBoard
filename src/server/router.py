import base64
from fastapi import APIRouter, Query, Body, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bilibili_api import Credential, user
from bilibili_api.login_v2 import QrCodeLogin, QrCodeLoginChannel
from src.manager import subscribe_manager
from src.database import Db
from src.utils import (
    setup_autostart,
    ResponseItem,
    bconfigItem,
    dyconfigItem,
    globalfigItem,
    async_worker,
    check_for_updates,
    PlaylistItem,
    logger)
from src.live import bili_manager, douyin_manager

router = APIRouter(tags=["api"])
qr_code_login: QrCodeLogin


class BiliCredential(BaseModel):
    id: int
    enable: bool


@router.get("/get_bili_config", response_model=ResponseItem)
async def get_bili_config():
    config = await async_worker.run_db_operation(Db.get_bconfig())
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(config)})


@router.post("/add_or_update_bili_config", response_model=ResponseItem)
async def add_or_update_bili_config(background_tasks: BackgroundTasks, data: bconfigItem = Body(..., embed=True)):
    result = await async_worker.run_db_operation(Db.add_or_update_bili_config(**data.__dict__))
    msg = "设置成功" if result > 0 else "设置失败"
    code = 0 if result > 0 else -1
    if result > 0:
        background_tasks.add_task(bili_manager.restart)
    return JSONResponse(status_code=200, content={"code": code, "msg": msg, "data": result})


@router.get("/get_bili_credential_list", response_model=ResponseItem)
async def get_bili_credential_list():
    query_list = await async_worker.run_db_operation(Db.get_bcredential_list())
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
    result = await async_worker.run_db_operation(Db.get_bcredential(pk=id))
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
            await async_worker.run_db_operation(Db.update_bcredential(pk=result.id, **new_dic))
        return ResponseItem(code=0, msg="刷新成功", data=None)
    return ResponseItem(code=-1, msg="fail", data=None)


@router.post("/delete_bili_credential", response_model=ResponseItem)
async def delete_bili_credential(id: int = Body(..., embed=True)):
    result = await async_worker.run_db_operation(Db.delete_bcredential(pk=id))
    if result:
        return ResponseItem(code=0, msg="删除成功", data=None)
    else:
        return ResponseItem(code=-1, msg="删除失败", data=None)


@router.post("/update_bili_credential")
async def update_bili_credential(background_tasks: BackgroundTasks, data: BiliCredential = Body(..., embed=True)):
    result = await async_worker.run_db_operation(Db.update_bcredential(pk=data.id, enable=data.enable))
    if result:
        background_tasks.add_task(bili_manager.restart)
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
        cred = await async_worker.run_db_operation(Db.get_bcredential(uid=uid))
        if not cred:
            await async_worker.run_db_operation(Db.add_bcredential(**model_dic))
        else:
            new_dic["enable"] = cred.enable
            await async_worker.run_db_operation(Db.update_bcredential(pk=cred.id, **model_dic))
        qr_code_login = None
        return ResponseItem(code=0, msg="success", data=None)
    return ResponseItem(code=0, msg="qr_state", data={"data": qr_state.value})


@router.get("/get_dy_config")
async def get_dy_config():
    result = await async_worker.run_db_operation(Db.get_dy_config())
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(result)})


@router.post("/add_or_update_dy_config", response_model=ResponseItem)
async def add_or_update_dy_config(background_tasks: BackgroundTasks, data: dyconfigItem = Body(..., embed=True)):
    result = await async_worker.run_db_operation(Db.add_or_updae_dy_config(**data.__dict__))
    msg = "设置成功" if result > 0 else "设置失败"
    code = 0 if result > 0 else -1
    if result > 0:
        background_tasks.add_task(douyin_manager.restart)
    return JSONResponse(status_code=200, content={"code": code, "msg": msg, "data": result})


@router.get("/get_global_config")
async def get_global_config():
    result = await async_worker.run_db_operation(Db.get_gloal_config())
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(result)})


@router.post("/add_or_update_global_config")
async def add_or_update_global_config(background_tasks: BackgroundTasks, data: globalfigItem = Body(..., embed=True)):
    if data.startup is not None:
        startup_result = setup_autostart(data.startup)
        if not startup_result:
            return ResponseItem(code=-1, msg="开机启动更新失败", data=None)
    result = await async_worker.run_db_operation(Db.add_or_update_gloal_config(**data.__dict__))
    if result > 0:
        code = 0
        msg = "设置成功"
        background_tasks.add_task(subscribe_manager.start_subscribe) if data.check_update else background_tasks.add_task(subscribe_manager.cancel_subscribe, "check_updates")
    else:
        code = -1
        msg = "设置失败"
    return JSONResponse(status_code=200, content={"code": code, "msg": msg, "data": result})


@router.get("/get_history_list")
async def get_history_list(uname: str = Query(...),
                           song_name: str = Query(...),
                           source: str = Query(...),
                           start_time: int = Query(...),
                           end_time: int = Query(...),
                           page: int = Query(1),
                           size: int = Query(20)):
    if not uname:
        uname = None
    if not song_name:
        song_name = None
    if source == "all":
        source = None
    if start_time is None or start_time == 0:
        start_time = None
    if end_time is None or end_time == 0:
        end_time = None
    total, songs = await async_worker.run_db_operation(Db.get_song_history_page(uname, song_name, source, start_time, end_time, page, size))
    return ResponseItem(code=0, msg=None, data={"total": total, "rows": jsonable_encoder(songs)})


@router.get("/check_updates")
async def check_update():
    result = await check_for_updates()
    return ResponseItem(code=0, msg=None, data=result)


@router.get("/get_playlist_list")
async def get_playlist_list(keyword: str = Query(...),
                            page: int = Query(1),
                            size: int = Query(20)):
    total, playlists = await async_worker.run_db_operation(Db.get_playlist_page(keyword, page, size))
    return ResponseItem(code=0, msg=None, data={"total": total, "rows": jsonable_encoder(playlists)})


@router.get("/get_playlist")
async def get_playlist(id: int):
    result = await async_worker.run_db_operation(Db.get_playlist(id))
    return ResponseItem(code=0, msg=None, data={"data": jsonable_encoder(result)})


@router.post("/add_or_update_playlist")
async def add_or_update_playlist(data: PlaylistItem = Body(..., embed=True)):
    result = await async_worker.run_db_operation(Db.add_or_update_playlist(**data.__dict__))
    msg = "操作成功" if result > 0 else "操作失败"
    code = 0 if result > 0 else -1
    return JSONResponse(status_code=200, content={"code": code, "msg": msg, "data": result})


@router.post("/delete_playlist")
async def delete_playlist(data: list[int] = Body(..., embed=True)):
    result = await async_worker.run_db_operation(Db.delete_playlist(data))
    msg = "操作成功" if result > 0 else "操作失败"
    code = 0 if result > 0 else -1
    return ResponseItem(code=code, msg=msg, data=None)


@router.post("/import_playlist")
async def import_playlist(data: list[PlaylistItem] = Body(..., embed=True)):
    code = 0
    msg = "操作成功"
    try:
        objects: dict[str, any] = []
        model_fields = ["song_name", "singer", "is_sc", "sc_price", "language", "tag", "create_time"]
        for item in data:
            model_dic = {k: v for k, v in item.__dict__.items() if v is not None and k in model_fields}
            objects.append(model_dic)
        await async_worker.run_db_operation(Db.bulk_add_playlist(objects))
    except Exception as ex:
        logger.exception(f"bulk add playlist exception: {ex}")
        code = -1
        msg = "操作失败"
    else:
        return ResponseItem(code=code, msg=msg, data=None)
