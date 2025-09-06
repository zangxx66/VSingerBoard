export type ResponseModel = {
    code: number
    msg: string
    data: any
}

export type DanmakuModel = {
    uid: number
    uname: string
    msg: string
    medal_level: number
    medal_name: string
    guard_level: number
    send_time: number
    price?: number
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