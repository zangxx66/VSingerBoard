<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watchEffect } from "vue"
import { RouterView } from "vue-router"
import router from "@/router"
import zhCn from "element-plus/es/locale/lang/zh-cn"
import { Minus, Close, HomeFilled, Tools, List, InfoFilled, Sunny, Moon } from "@element-plus/icons-vue"
import ContextMenu from '@imengyu/vue3-context-menu'
import { ElLoading, ElMessage, ElMessageBox, type MenuItemInstance } from "element-plus"
import { request } from "@/api"
import { toggleDark, checkUpdate, pasteToElement } from "@/utils"
import { useIntervalStore, useThemeStore } from "@/stores"
import { useClipboard } from "@vueuse/core"

const active = ref("0")
const isCollapse = ref(false)
const intervalStore = useIntervalStore()
const themeStore = useThemeStore()
const { copy } = useClipboard()
const cardConfig = {
  shadow: "always"
}

const dialogConfig = {
  alignCenter: true,
  draggable: true,
  overflow: false,
  transition: "el-fade-in"
}

const messageConfig = {
  offset: 70,
  plain: true
}

// 新手教程
const globalConfig = reactive<GlobalConfigModel>({
  id: 0,
  dark_mode: false,
  check_update: false,
  startup: false,
  notification: false,
  navSideTour: false
})
const navSideTour = ref(false)
const homeRef = ref<MenuItemInstance>()
const settingsRef = ref<MenuItemInstance>()
const themeRef = ref<MenuItemInstance>()
const collapseRef = ref<MenuItemInstance>()
const minusRef = ref<MenuItemInstance>()
const quitRef = ref<MenuItemInstance>()
const finishTour = () => {
  updateTourStatus()
}
const closeTour = async() => {
  await nextTick()
  if(globalConfig.navSideTour) return
  updateTourStatus()
}
const updateTourStatus = () => {
  globalConfig.navSideTour = true
  request
  .addOrUpdateGlobalConfig({data: globalConfig})
  .then(response => {
    const resp = response.data as ResponseModel
    if(resp.code != 0){
      ElMessage.warning(resp.msg || "保存失败")
    }
  })
  .catch(error => {
    ElMessage.error(error)
  })
  .finally(() => {
    navSideTour.value = false
  })
}
watchEffect(() => {
  if(navSideTour.value){
    globalConfig.navSideTour = false
  }
})

/**
 * 跳转到指定页面
 * @param {string} name 路由的name
 */
const goto = (name: string) => {
  router.push({ name: name })
}

/**
 * 右用右键菜单事件
 * @param {MouseEvent} e 右用事件
 */
const onContextMenu = async (e: MouseEvent) => {
  e.preventDefault()
  const selectTxt = window.getSelection()?.toString()
  const activeElement = document.activeElement as HTMLElement
  const isFocusInput = activeElement instanceof HTMLInputElement || activeElement instanceof HTMLTextAreaElement
  const isBundle = await window.pywebview.api.is_bundle()

  let hasClipboardText = false
  const clipboardItems = await window.pywebview.api.check_clipboard()
  if(clipboardItems && clipboardItems.length > 0){
    hasClipboardText = true
  }

  const items = [{
    label: "拷贝",
    disabled: !selectTxt,
    onClick: () => {
      if (selectTxt) {
        copy(selectTxt)
        ElMessage.success("拷贝成功")
      }
    }
  }, 
  {
    label: "粘贴",
    disabled: !isFocusInput || !hasClipboardText,
    onClick: () => { 
      pasteToElement(activeElement)
    }
  }]

  if (!isBundle) {
    items.push({
      label: "重新加载",
      disabled: false,
      onClick: () => {
        intervalStore.clearAllIntervals()
        window.pywebview.api.reload()
      }
    })
  }

  ContextMenu.showContextMenu({
    x: e.x,
    y: e.y,
    theme: isDarktheme.value ? "mac dark" : "mac",
    zIndex: 100,
    minWidth: 230,
    items: items
  })
}

/**
 * 最小化应用
 * @returns {void} 无返回值
 */
const minus = (): void => {
  window.pywebview.api.minus_window()
  active.value = "0"
}

/**
 * 退出应用
 * @returns {Promise<void>} 退出应用 Promise
 */
const quit = (): void => {
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
      intervalStore.clearAllIntervals()
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
const initGlobalConfig = async (): Promise<void> => {
  request.getGlobalConfig({}).then(response => {
    const resp = response.data as ResponseModel
    if (resp.code != 0) {
      ElMessage.warning(resp.msg)
    } else {
      const data = resp.data.data
      if (data) {
        const model = data as GlobalConfigModel
        Object.assign(globalConfig, model)
        toggleDark(model.dark_mode)
        themeStore.setDarkTheme(model.id, model.dark_mode)
        if (model.check_update) {
          checkUpdate()
          intervalStore.addInterval("check_update", checkUpdate, 1000 * 60 * 60 * 6)
        }
        if(!model.navSideTour){
          navSideTour.value = true
        }
      }else{
        navSideTour.value = true
      }
    }
  })
    .catch(error => {
      ElMessage.error(error)
      console.error("获取全局配置失败", error)
    })
}

const mainStyle = computed(() => {
  return {
    left: isCollapse.value ? '64px' : '200px'
  }
})

const asideStyle = computed(() => {
  return {
    width: isCollapse.value ? '64px' : '200px'
  }
})

const isDarktheme = computed(() => {
  return themeStore.getDarkTheme()
})

onMounted(() => {
  setTimeout(() => {
    initGlobalConfig()
  }, 1000)
})

</script>

<template>
  <el-container class="layout-container-demo">
    <el-aside :style="asideStyle">
      <el-menu default-active="0" :collapse="isCollapse" class="layout-aside-menu">
        <el-menu-item index="0" @click="goto('home')" ref="homeRef">
          <el-icon>
            <HomeFilled />
          </el-icon>
          <template #title>点歌板</template>
        </el-menu-item>
        <el-menu-item index="1" @click="goto('settings')" ref="settingsRef">
          <el-icon>
            <Tools />
          </el-icon>
          <template #title>设置</template>
        </el-menu-item>
        <el-menu-item index="2" @click="goto('changelog')">
          <el-icon>
            <List />
          </el-icon>
          <template #title>更新日志</template>
        </el-menu-item>
        <el-menu-item index="3" @click="goto('about')">
          <el-icon>
            <InfoFilled />
          </el-icon>
          <template #title>关于</template>
        </el-menu-item>
        <el-menu-item index="4" ref="themeRef">
          <el-switch v-model="isDarktheme" :active-action-icon="Moon" :inactive-action-icon="Sunny"
            style="--el-switch-on-color: var(--bg-color-mute)" @change="themeStore.updateConfig(!isDarktheme)" />
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-header class="pywebview-drag-region">
      <el-menu :default-active="active" mode="horizontal" :ellipsis="false" class="toolbar">
        <el-menu-item index="0" @click="isCollapse = !isCollapse" ref="collapseRef">
          <template v-if="isDarktheme">
            <img src="/assets/images/logo_night.png" alt="logo" style="width:100px;" />
          </template>
          <template v-else>
            <img src="/assets/images/logo.png" alt="logo" style="width:100px;" />
          </template>
        </el-menu-item>
        <el-menu-item index="1" @click="minus" ref="minusRef">
          <el-icon>
            <Minus />
          </el-icon>
        </el-menu-item>
        <el-menu-item index="2" @click="quit" ref="quitRef">
          <el-icon>
            <Close />
          </el-icon>
        </el-menu-item>
      </el-menu>
    </el-header>

    <el-main @contextmenu="onContextMenu" :style="mainStyle">
      <el-config-provider :locale="zhCn" :card="cardConfig" :dialog="dialogConfig" :message="messageConfig">
        <router-view v-slot="{ Component }">
          <keep-alive :include="['Home']">
            <component :is="Component" />
          </keep-alive>
        </router-view>
        <el-backtop :right="100" :bottom="100" />
        <!-- el-tour组件的finish会同时触发close事件 -->
        <el-tour v-model="navSideTour" @close="closeTour" @finish="finishTour" :target-area-clickable="false"
          :close-on-press-escape="false">
          <el-tour-step title="提示" description="欢迎使用抖破点歌姬"></el-tour-step>
          <el-tour-step title="提示" description="这里是点歌，可以查看抖和破站的点歌列表" placement="right"
            :target="homeRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="这里是设置，可以设置抖和破站的直播间监听" placement="right"
            :target="settingsRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="这是主题开关，可以切换主题" placement="right" :target="themeRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="点击这里可以收缩/展开侧边栏" placement="bottom"
            :target="collapseRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="点击这里最小化" placement="bottom" :target="minusRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="点击这里退出" placement="bottom" :target="quitRef?.$el"></el-tour-step>
        </el-tour>
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

/* Position the aside itself, not the menu */
.layout-container-demo .el-aside {
  position: fixed;
  left: 0;
  top: 60px;
  bottom: 0;
  z-index: 90;
  transition: width 0.3s ease-in-out;
}

/* The menu should fill the aside */
.layout-aside-menu {
  height: 100%;
}

.layout-aside-menu:not(.el-menu--collapse) {
  width: 200px;
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
  position: absolute;
  top: 60px;
  right: 0;
  bottom: 0;
  height: calc(100vh - 60px);
  overflow: hidden;
  transition: left 0.3s ease-in-out;
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
