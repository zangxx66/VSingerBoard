/// <reference types="vite/client" />
declare interface Window {
    pywebview: {
        api: {
            reload: () => void
            minus_window: () => void
            on_closing: () => void
            update_verion: () => Promise<UpdateModel>
            get_bili_ws_status: () => Promise<number>
            get_dy_ws_status: () => Promise<number>
            get_version: () => Promise<string>
            get_danmu: () => Promise<Array<DanmakuModel>>
            get_dy_danmu: () => Promise<Array<DanmakuModel>>
            send_notification: (title: string, message: string) => void
            is_bundle: () => Promise<boolean>
            check_clipboard: () => Promise<string>
        }
        token: string
    }
}