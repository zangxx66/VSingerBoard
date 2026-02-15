import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ContextMenu from '@imengyu/vue3-context-menu'
import { VueQueryPlugin, type VueQueryPluginOptions } from '@tanstack/vue-query'
import 'nprogress/nprogress.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/base.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
import '@unocss/reset/normalize.css'
import 'uno.css'

const app = createApp(App)

const vueQueryPluginOptions: VueQueryPluginOptions = {
  queryClientConfig: {
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
      },
    },
  },
}

app.use(createPinia())
.use(router)
.use(ContextMenu)
.use(VueQueryPlugin, vueQueryPluginOptions)
.mount("#app")
