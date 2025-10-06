type ResponseModel = {
    code: number
    msg: string
    data: any
}

type DanmakuModel = {
    uid: number
    uname: string
    msg: string
    send_time: number
    source: string
    html?: string
}

type SubscribeModel = {
    id: number
    room_id: number
    source: string
    create_time: number
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
}

type DyDanmuModel = {
    user_id: number
    user_name: string
    content: string
    level: number
    fans_club_data: any
}

type GlobalConfigModel = {
    id: number
    dark_mode: boolean
    check_update: boolean
    startup: boolean
    notification: boolean
    navSideTour: boolean
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
}
