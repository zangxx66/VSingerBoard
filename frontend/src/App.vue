<script setup lang="ts">
import { ref, onMounted } from "vue"
import { RouterView } from "vue-router"
import router from "@/router"
import zhCn from "element-plus/es/locale/lang/zh-cn"
import { Minus, Close } from "@element-plus/icons-vue"
import ContextMenu from '@imengyu/vue3-context-menu'
import { ElLoading, ElMessage, ElMessageBox, ElNotification } from "element-plus"
import { request } from "@/api"
import type { ResponseModel, GlobalConfigModel } from "@/types"
import { toggleDark } from "@/utils"

const active = ref("0")
const cardConfig = {
  shadow: "always"
}

const dialogConfig = {
  alignCenter: true,
  draggable: true,
  overflow: false,
  transition: "el-fade-in"
}

/**
 * 右用右键菜单事件
 * @param {MouseEvent} e 右用事件
 */
const onContextMenu = async (e: MouseEvent) => {
  e.preventDefault()
  const selectTxt = window.getSelection()?.toString()
  ContextMenu.showContextMenu({
    x: e.x,
    y: e.y,
    theme: "mac",
    zIndex: 100,
    minWidth: 230,
    items: [
      {
        label: "重新加载",
        onClick: () => {
          request.reload()
        }
      },
      {
        label: "拷贝",
        disabled: !selectTxt,
        onClick: () => {
          if (selectTxt) {
            // @ts-ignore
            window.pywebview.api.copy_to_clipboard(selectTxt)
            ElMessage.success("拷贝成功")
          }
        }
      },
    ]
  })
}

/**
 * 最小化应用
 * @returns {void} 无返回值
 */
const minus = () => {
  // @ts-ignore
  window.pywebview.api.minus_window()
  active.value = "0"
}

/**
 * 退出应用
 * @returns {Promise<void>} 退出应用 Promise
 */
const quit = () => {
  ElMessageBox.confirm(
    "是否退出?",
    "提示",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(() => {
      const loading = ElLoading.service({
        lock: true,
        text: "正在退出...",
        background: "rgba(0, 0, 0, 0.7)"
      })
      // @ts-ignore
      window.pywebview.api.on_closing()
    })
    .catch((error) => {
      if ('string' == typeof error && 'cancel' == error) return
      ElMessage.error(error)
    })
}

/**
 * 初始化全局配置
 * 从服务器获取全局配置，并将其保存到应用程序中
 * 如果获取失败，将显示错误信息
 * @returns {Promise<void>} 无返回值 Promise
 */
const initGlobalConfig = () => {
  request.getGlobalConfig({}).then(response => {
    const resp = response.data as ResponseModel
    if(resp.code != 0){
      ElMessage.warning(resp.msg)
    }else{
      const data = resp.data.data
      if(data != null){
        const model = data as GlobalConfigModel
        toggleDark(model.dark_mode)
        if(model.check_update){
          // @ts-ignore
          return window.pywebview.api.check_for_updates()
        }
      }
    }
  })
  .then(response => {
    if(!response)return
    if(response.code == 0){
      if(response.url != ""){
        ElNotification({
          title: "提示",
          message: response.msg,
          type: "primary",
          position: "bottom-right"
        })
      }
    }else{
      ElMessage.warning(response.msg)
    }
  })
  .catch(error => {
    ElMessage.error(error)
    console.error("获取全局配置失败", error)
  })
}

onMounted(() => {
  const dom = document.querySelector(".layout-container-demo .el-main") as HTMLElement
  dom.style.width = window.innerWidth + "px"
  initGlobalConfig()
})
</script>

<template>
  <el-container class="layout-container-demo">
    <el-header class="glassmorphism pywebview-drag-region">
      <el-menu :default-active="active" mode="horizontal" :ellipsis="false" class="toolbar">
        <el-menu-item index="0">
          <img src="/assets/images/logo.png" alt="logo" style="width:100px;" />
        </el-menu-item>
        <el-menu-item index="1" @click="minus">
          <el-icon>
            <Minus />
          </el-icon>
        </el-menu-item>
        <el-menu-item index="2" @click="quit">
          <el-icon>
            <Close />
          </el-icon>
        </el-menu-item>
      </el-menu>
    </el-header>

    <el-main @contextmenu="onContextMenu">
      <el-config-provider :locale="zhCn" :card="cardConfig" :dialog="dialogConfig">
        <RouterView></RouterView>
        <el-backtop :right="100" :bottom="100" />
      </el-config-provider>
    </el-main>
  </el-container>
</template>

<style scoped>
.el-menu--horizontal>.el-menu-item:nth-child(1) {
  margin-right: auto;
}

.layout-container-demo {
  width: 100%;
  height: 100%;
}

.layout-container-demo .el-header {
  position: fixed;
  width: 100%;
  left: 0;
  top: 0;
  right: 0;
  z-index: 100;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: var(--el-text-color-primary);
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
}

.layout-container-demo .el-menu {
  border-right: none;
}

.layout-container-demo .el-main {
  height: calc(100vh - 30px);
  left: 0;
  position: absolute;
  overflow: hidden;
}

.layout-container-demo .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  width: 100%;
  right: 0;
  background-color: transparent;
  text-align: right;
  font-size: 24px;
}
</style>
