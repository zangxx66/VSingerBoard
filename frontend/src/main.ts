import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ContextMenu from "@imengyu/vue3-context-menu"
import linkIcon from "@/components/common/linkIcon"
import fansClub from "@/components/common/fansClub"
import fansMedal from "@/components/common/fansMedal"
import lineHeader from "@/components/common/lineHeader"
import 'nprogress/nprogress.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/base.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
import "@/assets/main.css"

const app = createApp(App)

app.use(createPinia())
.use(router)
.use(ContextMenu)
.component("link-icon", linkIcon)
.component("fans-club", fansClub)
.component("fans-medal", fansMedal)
.component("line-header", lineHeader)
.mount("#app")
