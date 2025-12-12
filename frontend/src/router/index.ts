import {
  createRouter,
  createWebHistory,
  isNavigationFailure,
  type RouteRecordRaw,
} from 'vue-router'
import { start, stop } from '@/utils'
import { ElMessage } from 'element-plus'

const pages = import.meta.glob('../views/**/index.vue', {
  import: 'default',
})

const routesByLayout = Object.keys(pages).reduce<{
  default: RouteRecordRaw[]
  blank: RouteRecordRaw[]
}>(
  (acc, path) => {
    const routePath = path.replace('../views', '').replace('/index.vue', '') || '/'
    const name = routePath.split('/').filter(Boolean).join('-') || 'index'

    if (name === 'danmaku') {
      acc.blank.push({
        path: '',
        name,
        component: () => import(path),
      })
    } else {
      acc.default.push({
        path: name === 'home' ? '' : name,
        name,
        component: () => import(path),
      })
    }
    return acc
  },
  { default: [], blank: [] },
)

const routerList: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('../components/layout/defaultLayout.vue'),
    children: routesByLayout.default,
  },
  {
    path: '/danmaku',
    component: () => import('../components/layout/blankLayout.vue'),
    children: routesByLayout.blank,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routerList,
})

router.beforeEach(async (toString, from) => {
  start()
  return true
})

router.afterEach((to, from, failure) => {
  stop()
  if (isNavigationFailure(failure) && to.name != from.name) {
    ElMessage.warning(`failled navigation:${failure}`)
  }
})

export default router
