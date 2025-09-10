import { createRouter, createWebHistory, isNavigationFailure } from 'vue-router'
import { start, stop } from "@/utils"
import { ElMessage } from "element-plus"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/Home.vue")
    },
  ],
})

router.beforeEach(async (toString, from) => {
    start()
    return true
})

router.afterEach((to, from, failure) => {
  stop()
  if(isNavigationFailure(failure)){
    ElMessage.warning(`failled navigation:${failure}`)
  }
})

export default router
