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