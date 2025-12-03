import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ContextMenu from "@imengyu/vue3-context-menu"
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
.mount("#app")
