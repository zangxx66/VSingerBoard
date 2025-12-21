type ResponseModel = {
    code: number
    msg: string
    data: any
}

type DanmakuModel = {
    msg_id: number
    uid: number
    uname: string
    msg: string
    send_time: number
    source: string
    html?: string
    medal_name: string
    medal_level: number
    guard_level: number,
    status?: number
}

type BiliConfigModel = {
    id: number
    room_id: number
    modal_level: number
    user_level: number
    sing_prefix: string
    sing_cd: number
}

type BiliCredentialModel = {
    id: number
    uname: string
    avatar: string
    uid: number
    enable: boolean
}

type DyConfigModel = {
    id: number
    room_id: number
    sing_prefix: string
    sing_cd: number
    fans_level: number
}

type GlobalConfigModel = {
    id: number
    dark_mode: boolean
    check_update: boolean
    startup: boolean
    notification: boolean
    navSideTour: boolean
    collapse: boolean
}

type UpdateModel = {
    code: number
    msg: string
    version: string
    url: string
    body: string
    published_at: string
}

type LiveModel = {
    douyin_romm_id: number
    bilibili_room_id: number
    douyin_ws_status: number
    bilibili_ws_status: number
}

type WsModel = {
    type: string
    data?: any
}

type DelListModel = {
    msg_id: number
    uid: number
    uname: string
    song_name: string
}

type SongHistoryModel = {
    id: number
    uid: number
    uname: string
    song_name: string
    source: string
    create_time: number
    create_time_str?: string
}

type PlaylistModel = {
    id: number
    song_name: string
    singer: string
    is_sc: boolean
    sc_price: number
    language: string
    tag: string
    create_time: number
    checked?: boolean
}

type DynamicObject = {
    [key: string]: string | number | Array<any> | boolean | null | undefined
}

type ImportColumn = {
    header: string
    key: string
    type: string
}
