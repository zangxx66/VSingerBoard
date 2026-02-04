import {
  createRouter,
  createWebHistory,
  isNavigationFailure,
} from 'vue-router'
import { routes } from 'vue-router/auto-routes'
import { start, stop } from '@/utils'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((toString, from, next) => {
  start()
  if (toString.path == "/"){
    next({ name: "/home/" })
  }
  next()
})

router.afterEach((to, from, failure) => {
  stop()
  if (isNavigationFailure(failure) && to.name != from.name) {
    ElMessage.warning(`failled navigation:${failure}`)
  }
})

export default router
