<script setup lang="tsx">
import zhCn from "element-plus/es/locale/lang/zh-cn"
import { 
  HomeFilled, 
  Tools, 
  List, 
  InfoFilled, 
  Sunny, 
  Moon, 
  Calendar, 
  Collection, 
} from "@element-plus/icons-vue"
import ContextMenu from '@imengyu/vue3-context-menu'
import { 
  ElMessage, 
  type MenuItemInstance, 
  type CardConfigContext, 
  type TabPaneName, 
} from "element-plus"

defineOptions({
  name: "defaultLayout"
})

const themeStore = useThemeStore()
const route = useRoute() // 当前路由实例
const router = useRouter() // 路由器实例
const cardConfig: CardConfigContext = {
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

const activeTabName = ref("/")
const activeMenu = ref("0")
const openTabs = ref<TabItem[]>([])
// 缓存已打开的tab
const components = computed(() => {
  return openTabs.value.map(item => item.componentName).filter(Boolean)
})

const menuItemList = [
  {
    title: "点歌板",
    icon: <HomeFilled />,
    routerName: "/",
    ref: "homeRef"
  },
  {
    title: "点歌记录",
    icon: <Calendar />,
    routerName: "/history",
    ref: "historyRef"
  },
  {
    title: "歌单管理",
    icon: <Collection />,
    routerName: "/playlist",
    ref: "playlistRef"
  },
  {
    title: "更新日志",
    icon: <List />,
    routerName: "/changelog"
  },
  {
    title: "设置",
    icon: <Tools />,
    routerName: "/settings",
    ref: "settingsRef"
  },
  {
    title: "关于",
    icon: <InfoFilled />,
    routerName: "/about"
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

const { data: globalConfigData, isFetching } = useGetGlobalConfig()

/**
 * 初始化全局配置
 * 从服务器获取全局配置，并将其保存到应用程序中
 * 如果获取失败，将显示错误信息
 */
const initGlobalConfig = () => {
  const model = globalConfigData.value
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

const globalConfigMutation = useMutation({
  mutationFn: async (params: GlobalConfigModel) => await addOrUpdateGlobalConfig({ data: params }),
  onSuccess: (data) => {
    if (data.code != 0) {
      ElMessage.warning(data.msg || "请求异常")
    } else {
      globalConfig.id = data.data
    }
  },
  onError: (error) => {
    ElMessage.error(error.message)
  }
})
const navSideTour = ref(false)
const homeRef = ref<MenuItemInstance | null>()
const historyRef = ref<MenuItemInstance | null>()
const settingsRef = ref<MenuItemInstance | null>()
const themeRef = ref<MenuItemInstance | null>()
const mainRef = useTemplateRef("mainRef")

const finishTour = () => {
  globalConfig.navSideTour = true
  globalConfigMutation.mutate(globalConfig)
  navSideTour.value = false
}

const closeTour = async () => {
  // 等待dom更新
  await nextTick()
  // 如果finish已经关闭tour，什么也不做
  if (globalConfig.navSideTour) return
  globalConfig.navSideTour = true
  globalConfigMutation.mutate(globalConfig)
  navSideTour.value = false
}

const updateActiveMenu = (routeName: string) => {
  const menuItemIndex = menuItemList.findIndex(item => item.routerName == routeName)
  activeMenu.value = menuItemIndex.toString()
}

/**
 * 跳转到指定页面
 * @param {string} name 路由的name
 */
const goto = (name: string) => {
  if (route.path == name) {
    globalConfig.collapse = !globalConfig.collapse
    globalConfigMutation.mutate(globalConfig)
    return
  }

  changeTab(name as TabPaneName)
}

/**
 * 切换标签页
 * @param name 
 */
const changeTab = (name: TabPaneName) => {
  const tabName = name.toString()

  const currentRouteTitle = menuItemList.find(item => item.routerName == tabName)?.title || route.path
  let tab = openTabs.value.find(tab => tab.name === tabName)

  if (!tab) {
    tab = {
      name: tabName,
      title: currentRouteTitle,
      path: tabName,
      closable: tabName !== "/", 
      componentName: tabName == "/" ? "home" : tabName.replaceAll('/', '')
    }
    openTabs.value.push(tab)
  }

  activeTabName.value = tabName
  router.push({ path: tabName })
  updateActiveMenu(tabName)
} 

/**
 * 移除标签页
 * @param {TabPaneName} targetTabName 要移除的标签页的name
 */
const removeTab = (targetTabName: TabPaneName) => {
  const tabs = openTabs.value
  const tabName = targetTabName.toString()
  let newActiveTabName = activeTabName.value

  if (newActiveTabName === tabName) {
    tabs.forEach((tab, index) => {
      if (tab.name === tabName) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) {
          newActiveTabName = nextTab.name
        } else {
          // 如果没有其他标签页，则回到首页
          newActiveTabName = "/"
        }
      }
    })
  }

  openTabs.value = tabs.filter(tab => tab.name !== tabName)
  activeTabName.value = newActiveTabName
  router.push({ path: newActiveTabName })
  updateActiveMenu(newActiveTabName)
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

const updateTheme = () => {
  globalConfig.dark_mode = !globalConfig.dark_mode
  globalConfigMutation.mutate(globalConfig)
  toggleDark(globalConfig.dark_mode)
  themeStore.setDarkTheme(globalConfig.dark_mode)
}

const findNavIcon = (routeName: string) => {
  return menuItemList.find(item => item.routerName == routeName)?.icon || <HomeFilled />
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

watch(isFetching, () => {
  if (globalConfigData.value) initGlobalConfig()
}, { once: true })

onMounted(() => {
  const currentRouteTitle = menuItemList.find(item => item.routerName == route.path)?.title || route.name
  openTabs.value.push({
    name: route.path,
    title: currentRouteTitle,
    path: route.path,
    closable: route.path !== "/",
    componentName: route.name as string
  })
  activeTabName.value = route.path
})
</script>

<template>
  <el-container class="layout-container-demo">
    <el-aside :style="asideStyle">
      <el-menu :default-active="activeMenu" :collapse="globalConfig.collapse" class="layout-aside-menu">
        <template v-for="item, index in menuItemList" :key="index">
          <el-menu-item :ref="item.ref || undefined" :index="index.toString()" @click="goto(item.routerName)">
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
        <el-menu-item ref="themeRef" :index="(menuItemList.length + 1).toString()" @click="updateTheme">
          <el-icon v-if="!isDarktheme">
            <Sunny />
          </el-icon>
          <el-icon v-if="isDarktheme">
            <Moon />
          </el-icon>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main ref="mainRef" :style="mainStyle" @contextmenu="onContextMenu">
      <el-config-provider :locale="zhCn" :card="cardConfig" :dialog="dialogConfig" :message="messageConfig">
        <el-tabs v-model="activeTabName" type="card" closable @tab-remove="removeTab" @tab-change="changeTab">
          <template v-for="item in openTabs" :key="item.name">
            <el-tab-pane :name="item.name" :closable="item.closable">
              <template #label>
                <span>
                  <el-icon style="vertical-align: middle">
                    <component :is="findNavIcon(item.path)" />
                  </el-icon>
                  <span style="vertical-align: middle;margin-left: 4px;">{{ item.title }}</span>
                </span>
              </template>
            </el-tab-pane>
          </template>
        </el-tabs>
        <router-view v-slot="{ Component }">
          <keep-alive :include="components">
            <component :is="Component" />
          </keep-alive>
        </router-view>
        <!-- 
        el-tour组件finish和close事件的的使用示例
        https://github.com/element-plus/element-plus/issues/22419 
        -->
        <el-tour
        v-model="navSideTour" :target-area-clickable="false" :close-on-press-escape="false" @close="closeTour"
          @finish="finishTour">
          <el-tour-step title="提示" description="欢迎使用点歌姬"></el-tour-step>
          <el-tour-step
          title="提示" description="这里是点歌，可以查看抖和破站的点歌列表" placement="right"
            :target="homeRef?.$el"></el-tour-step>
          <el-tour-step
          title="提示" description="这里是历史记录，可以查看历史点歌" placement="right"
            :target="historyRef?.$el"></el-tour-step>
          <el-tour-step
          title="提示" description="这里是设置，可以设置抖和破站的直播间监听" placement="right"
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
