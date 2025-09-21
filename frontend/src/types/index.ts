export type ResponseModel = {
    code: number
    msg: string
    data: any
}

export type DanmakuModel = {
    uid: number
    uname: string
    msg: string
    send_time: number
    source: string
}

export type SubscribeModel = {
    id: number
    room_id: number
    source: string
    create_time: number
}

export type BiliConfigModel = {
    id: number
    room_id: number
    modal_level: number
    user_level: number
    sing_prefix: string
    sing_cd: number
}

export type BiliCredentialModel = {
    id: number
    uname: string
    avatar: string
    uid: number
    enable: boolean
}

export type DyConfigModel = {
    id: number
    room_id: number
    sing_prefix: string
    sing_cd: number
}

export type DyDanmuModel = {
    user_id: number
    user_name: string
    content: string
    level: number
    fans_club_data: any
}


export type GlobalConfigModel = {
    id: number
    dark_mode: boolean
    check_update: boolean
    startup: boolean
}