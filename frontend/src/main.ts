import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ContextMenu from "@imengyu/vue3-context-menu"
import 'nprogress/nprogress.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/base.css'
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
import "@/assets/main.css"

const app = createApp(App)

app.use(router)
app.use(ContextMenu)
app.mount('#app')
