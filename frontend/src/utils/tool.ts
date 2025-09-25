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
