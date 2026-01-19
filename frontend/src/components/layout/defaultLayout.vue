<script setup lang="tsx">
import router from "@/router"
import zhCn from "element-plus/es/locale/lang/zh-cn"
import { HomeFilled, Tools, List, InfoFilled, Sunny, Moon, Calendar, Collection } from "@element-plus/icons-vue"
import ContextMenu from '@imengyu/vue3-context-menu'
import { ElMessage, type MenuItemInstance } from "element-plus"
import { request } from "@/api"
import { toggleDark, pasteToElement, copyToClipboard } from "@/utils"

const themeStore = useThemeStore()
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

const menuItemList = [
  {
    title: "点歌板",
    icon: <HomeFilled />,
    routerName: "home",
    ref: "homeRef"
  },
  {
    title: "点歌记录",
    icon: <Calendar />,
    routerName: "history",
    ref: "historyRef"
  },
  {
    title: "歌单管理",
    icon: <Collection />,
    routerName: "playlist",
    ref: "playlistRef"
  },
  {
    title: "更新日志",
    icon: <List />,
    routerName: "changelog"
  },
  {
    title: "设置",
    icon: <Tools />,
    routerName: "settings",
    ref: "settingsRef"
  },
  {
    title: "关于",
    icon: <InfoFilled />,
    routerName: "about"
  }
]

// 新手教程
const globalConfig = reactive<GlobalConfigModel>({
  id: 0,
  dark_mode: false,
  check_update: false,
  startup: false,
  notification: false,
  navSideTour: false,
  collapse: false
})
const navSideTour = ref(false)
const homeRef = ref<MenuItemInstance | null>()
const historyRef = ref<MenuItemInstance | null>()
const settingsRef = ref<MenuItemInstance | null>()
const themeRef = ref<MenuItemInstance | null>()
const mainRef = useTemplateRef("mainRef")
const finishTour = () => {
  globalConfig.navSideTour = true
  updateGlobalConfig()
  navSideTour.value = false
}
const closeTour = async () => {
  // 等待dom更新
  await nextTick()
  // 如果finish已经关闭tour，什么也不做
  if (globalConfig.navSideTour) return
  globalConfig.navSideTour = true
  updateGlobalConfig()
  navSideTour.value = false
}
const updateGlobalConfig = () => {
  request
    .addOrUpdateGlobalConfig({ data: globalConfig })
    .then(response => {
      const resp = response.data as ResponseModel
      if (resp.code != 0) {
        ElMessage.warning(resp.msg || "保存失败")
      } else {
        globalConfig.id = resp.data
      }
    })
    .catch(error => {
      ElMessage.error(error)
    })
}

/**
 * 跳转到指定页面
 * @param {string} name 路由的name
 */
const goto = (name: string) => {
  if (router.currentRoute.value.name == name) {
    globalConfig.collapse = !globalConfig.collapse
    updateGlobalConfig()
    return
  }
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

  let hasClipboardText = false
  const clipboardItems = await window.pywebview.api.check_clipboard()
  if (clipboardItems && clipboardItems.length > 0) {
    hasClipboardText = true
  }

  const items = [{
    label: "拷贝",
    disabled: !selectTxt,
    onClick: () => {
      if (selectTxt) {
        copyToClipboard(selectTxt)
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

  if (import.meta.env.DEV) {
    items.push({
      label: "重新加载",
      disabled: false,
      onClick: () => {
        window.pywebview.api.reload()
      }
    })
  }

  ContextMenu.showContextMenu({
    x: e.x,
    y: e.y,
    theme: isDarktheme.value ? "mac dark" : "mac",
    zIndex: 9999,
    minWidth: 230,
    items: items
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
      const model = resp.data.data
      if (model) {
        Object.assign(globalConfig, model)
        toggleDark(model.dark_mode)
        themeStore.setDarkTheme(model.dark_mode)
        if (!model.navSideTour) {
          navSideTour.value = true
        }
      } else {
        navSideTour.value = true
      }
    }
  })
    .catch(error => {
      ElMessage.error(error)
      console.error("获取全局配置失败", error)
    })
}

const updateTheme = () => {
  globalConfig.dark_mode = !globalConfig.dark_mode
  updateGlobalConfig()
  toggleDark(globalConfig.dark_mode)
  themeStore.setDarkTheme(globalConfig.dark_mode)
}

const mainStyle = computed(() => {
  return {
    left: globalConfig.collapse ? '64px' : '200px'
  }
})

const asideStyle = computed(() => {
  return {
    width: globalConfig.collapse ? '64px' : '200px'
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
      <el-menu default-active="0" :collapse="globalConfig.collapse" class="layout-aside-menu">
        <template v-for="item, index in menuItemList">
          <el-menu-item :index="`${index}`" @click="goto(item.routerName)" :ref="item.ref || undefined">
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
        <el-menu-item ref="themeRef" @click="updateTheme">
          <el-icon v-if="!isDarktheme">
            <Sunny />
          </el-icon>
          <el-icon v-if="isDarktheme">
            <Moon />
          </el-icon>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main @contextmenu="onContextMenu" :style="mainStyle" ref="mainRef">
      <el-config-provider :locale="zhCn" :card="cardConfig" :dialog="dialogConfig" :message="messageConfig">
        <router-view v-slot="{ Component }">
          <keep-alive :include="['home']">
            <component :is="Component" />
          </keep-alive>
        </router-view>
        <el-backtop :right="100" :bottom="100" />
        <!-- 
        el-tour组件finish和close事件的的使用示例
        https://github.com/element-plus/element-plus/issues/22419 
        -->
        <el-tour v-model="navSideTour" @close="closeTour" @finish="finishTour" :target-area-clickable="false"
          :close-on-press-escape="false">
          <el-tour-step title="提示" description="欢迎使用点歌姬"></el-tour-step>
          <el-tour-step title="提示" description="这里是点歌，可以查看抖和破站的点歌列表" placement="right"
            :target="homeRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="这里是历史记录，可以查看历史点歌" placement="right"
            :target="historyRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="这里是设置，可以设置抖和破站的直播间监听" placement="right"
            :target="settingsRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="这是主题开关，可以切换主题" placement="right" :target="themeRef?.$el"></el-tour-step>
          <el-tour-step title="提示" description="这里是主界面" placement="left" :target="mainRef?.$el"></el-tour-step>
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
  top: 30px;
  bottom: 0;
  z-index: 90;
  transition: width 0.3s ease-in-out;
  border-right: solid 1px var(--el-border-color-light);
  border-top: solid 1px var(--el-border-color-light);
  overflow: hidden;
}

/* The menu should fill the aside */
.layout-aside-menu {
  height: 100%;
}

.layout-aside-menu:not(.el-menu--collapse) {
  width: 200px;
}

.layout-container-demo .el-menu {
  border-right: none;
}

.layout-container-demo .el-main {
  position: absolute;
  top: 0px;
  right: 0;
  bottom: 0;
  height: calc(100vh - 0px);
  overflow: hidden;
  transition: left 0.3s ease-in-out;
}
</style>
