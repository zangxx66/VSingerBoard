/// <reference types="vite/client" />
declare interface Window {
    pywebview: {
        api: {
            /** 重新加载 */
            reload: () => void
            /** 最小化 */
            minus_window: () => void
            /** 退出应用 */
            on_closing: () => void
            /** 检查更新 */
            update_verion: () => Promise<UpdateModel>
            /** 获取bilibili websocket状态 */
            get_bili_ws_status: () => Promise<number>
            /** 获取抖音websocket状态 */
            get_dy_ws_status: () => Promise<number>
            /** 获取当前版本 */
            get_version: () => Promise<string>
            /** 获取bilibili点歌列表 */
            get_danmu: () => Promise<Array<DanmakuModel>>
            /** 获取抖音点歌列表 */
            get_dy_danmu: () => Promise<Array<DanmakuModel>>
            /** 是否是bundle */
            is_bundle: () => Promise<boolean>
            /** 检查剪贴板 */
            check_clipboard: () => Promise<string>
            /** 重新启动bilibili websocket */
            restart_bilibili_ws: () => void
            /** 重新启动抖音 websocket */
            restart_douyin_ws: () => void
            /** 获取直播配置 */
            get_live_config: () => Promise<LiveModel>
        }
        token: string
    }
}