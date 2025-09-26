import { ElMessage, ElNotification } from "element-plus"

/**
 * Check if there is a new version of the VSingerBoard application.
 *
 * This function will send a GET request to the GitHub Releases API to get the latest version of the VSingerBoard application.
 *
 * It will then compare the latest version with the current version and notify the user with a notification.
 *
 * If there is a new version, the notification will have a link to the latest release.
 *
 * If there is no new version, the notification will have a warning message.
 */
export const checkUpdate = async() => {
  const result = await window.pywebview.api.check_for_updates()
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