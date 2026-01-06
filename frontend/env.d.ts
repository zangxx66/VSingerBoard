/// <reference types="vite/client" />
declare interface Window {
    pywebview: {
        api: {
            /** 重新加载 */
            reload: () => void
            /** 获取当前版本 */
            get_version: () => Promise<string>
            /** 检查剪贴板 */
            check_clipboard: () => Promise<string>
            /** 重新启动bilibili websocket */
            restart_bilibili_ws: () => void
            /** 重新启动抖音 websocket */
            restart_douyin_ws: () => void
        }
        token: string
    }
}