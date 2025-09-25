/// <reference types="vite/client" />
declare interface Window {
    pywebview: {
        api: {
            reload: () => void
            copy_to_clipboard: (text: string) => void
            minus_window: () => void
            on_closing: () => void
            check_for_updates: () => Promise<any>
            get_bili_ws_status: () => Promise<number>
            get_dy_ws_status: () => Promise<number>
            get_version: () => Promise<string>
            get_danmu: () => Promise<Array<DanmakuModel>>
            get_dy_danmu: () => Promise<Array<DanmakuModel>>
            send_notification: (title: string, message: string) => void
            is_bundle: () => Promise<boolean>
        }
        token: string
    }
}