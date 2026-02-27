from typing import TypedDict, Optional, Dict, Any
from pydantic import BaseModel


class DanmuInfo(TypedDict):
    msg_id: int
    uid: int
    uname: str
    msg: str
    medal_level: int
    medal_name: str
    guard_level: int
    price: Optional[int]
    send_time: int
    status: Optional[int]


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
    fans_level: int


class globalfigItem(BaseModel):
    id: int
    dark_mode: Optional[bool] = None
    check_update: Optional[bool] = None
    startup: Optional[bool] = None
    notification: Optional[bool] = None
    navSideTour: Optional[bool] = None
    collapse: Optional[bool] = None


class WebsocketDataItem(BaseModel):
    type: str
    data: Any


class PlaylistItem(BaseModel):
    id: int
    song_name: str
    singer: str
    is_sc: bool
    sc_price: int
    language: str
    tag: str
    create_time: int


class BiliCredentialItem(BaseModel):
    id: int
    sessdata: str
    bili_jct: str
    buvid3: str
    buvid4: str
    dedeuserid: str
    ac_time_value: str
    uid: int
    enable: bool


class HistoryItem(BaseModel):
    id: int
    uid: int
    uname: str
    song_name: str
    source: str
    create_time: int
