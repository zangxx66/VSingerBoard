import {
  createRouter,
  createWebHistory,
  isNavigationFailure,
  type RouteRecordRaw,
} from 'vue-router'
import { routes } from 'vue-router/auto-routes'
import { ElMessage } from 'element-plus'
import { setupLayouts } from 'virtual:generated-layouts'

type CreateMutable<Type> = {
  -readonly [Property in keyof Type]: Type[Property]
}

type routeRecordType = CreateMutable<RouteRecordRaw>
const routeRecord: routeRecordType[] = [...routes]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: setupLayouts(routeRecord)
})

router.beforeEach(async (toString, _from) => {
  startProgress()
  if (navigator.userAgent != "pywebview" && toString.path != "/danmaku") {
    return false
  }
  else {
    return true
  }
})

router.afterEach((to, from, failure) => {
  stopProgress()
  if (isNavigationFailure(failure) && to.name != from.name) {
    ElMessage.warning(`failled navigation:${failure}`)
  }
})

export default router
