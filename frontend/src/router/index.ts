import { createRouter, createWebHistory, isNavigationFailure } from 'vue-router'
import { start, stop } from "@/utils"
import { ElMessage } from "element-plus"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: () => import("../components/layout/defaultLayout.vue"),
      children: [
        {
          path: "",
          name: "home",
          component: () => import("../views/Home.vue")
        },
        {
          path: "/settings",
          name: "settings",
          component: () => import("../views/Settings.vue")
        },
        {
          path: "/changelog",
          name: "changelog",
          component: () => import("../views/Changelog.vue")
        },
        {
          path: "/about",
          name: "about",
          component: () => import("../views/About.vue")
        },
      ]
    },
    {
      path: "/danmaku",
      component: () => import("../components/layout/blankLayout.vue"),
      children: [
        {
          path: "",
          name: "danmaku",
          component: () => import("../views/Danmaku.vue")
        }
      ]
    }
  ],
})

router.beforeEach(async (toString, from) => {
    start()
    return true
})

router.afterEach((to, from, failure) => {
  stop()
  if(isNavigationFailure(failure) && to.name != from.name){
    ElMessage.warning(`failled navigation:${failure}`)
  }
})

export default router
