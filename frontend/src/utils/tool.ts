import { ElMessage, ElNotification } from "element-plus"
import { emojiList } from "./emoji"
import { emoticons } from "./emoticons"

const emojiexp = /\[[\u4E00-\u9FA5A-Za-z0-9_]+\]/g
const { copy } = useClipboard()

/**
 * 检查VSingerBoard应用程序是否有新版本。
 *
 * 此函数将向GitHub Releases API发送GET请求，以获取VSingerBoard应用程序的最新版本。
 *
 * 然后，它将最新版本与当前版本进行比较，并通过通知告知用户。
 *
 * 如果有新版本，通知将包含指向最新版本的链接。
 *
 * 如果没有新版本，通知将显示警告消息。
 */
export const checkUpdate = async() => {
  const result = await window.pywebview.api.update_verion()
  if (result.code == 0 && result.url != "") {
        ElNotification({
          title: "提示",
          message: result.msg,
          type: "primary",
          position: "bottom-right",
          onClick: () => {
            const a = document.createElement("a")
            a.href = result.url
            a.target = "_blank"
            a.click()
          }
        })
      } else {
        ElMessage.warning(result.msg)
      }
}

export const pasteToElement = async(activeEl: HTMLElement | null) => {
  if(activeEl && (activeEl instanceof HTMLInputElement || activeEl instanceof HTMLTextAreaElement)){
    try{
      const text = await window.pywebview.api.check_clipboard()

      if("string" == typeof text){
        const el = activeEl as HTMLInputElement | HTMLTextAreaElement

        const start = el.selectionStart ?? el.value.length
        const end = el.selectionEnd ?? el.value.length

        el.value = el.value.substring(0, start) + text + el.value.substring(end)

        el.dispatchEvent(new Event("input", { bubbles: true, cancelable: true }))

        el.focus()
        const newCursorPos = start + text.length
        el.selectionStart = el.selectionEnd = newCursorPos
      }
    }catch(error){
      console.error(error)
    }
  }
}


export const processDanmaku = (list: DanmakuModel[], platform: "bilibili" | "douyin") => {
  list.forEach(item => {
    let result = item.msg
    const matchList = item.msg.match(emojiexp)
    if(matchList) {
      for(const value of matchList) {
        let emojiUrl: string | undefined
        if(platform == "bilibili") {
          const emoji = emoticons.find((e) => value === e.emoji)
          if (emoji) emojiUrl = emoji.url
        }else {
          const emoji = emojiList.find((item) => value === item.display_name)
          if (emoji) emojiUrl = emoji.url
        }
        if(emojiUrl) {
          result = result.replaceAll(
            value,
            `<img src="${emojiUrl}" referrerpolicy="no-referrer" width="20" />`
          )
        }
      }
      item.html = result
    }
  })
  return list
}


export const copyToClipboard = (text: string) => {
  copy(text)
}