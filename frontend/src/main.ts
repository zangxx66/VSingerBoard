import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import 'nprogress/nprogress.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/base.css'
import "@/assets/main.css"

const app = createApp(App)

app.use(router)

app.mount('#app')
