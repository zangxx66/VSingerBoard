<script setup lang="ts">
import { ref, computed } from "vue"
import { RouterView } from "vue-router"
import router from "@/router"
import zhCn from "element-plus/es/locale/lang/zh-cn"
import { ElMessage } from "element-plus"
import { HomeFilled, List, StarFilled, Share } from "@element-plus/icons-vue"

const active = ref(1)

const cardConfig = {
  shadow: "always"
}

const dialogConfig = {
  alignCenter: true,
  draggable: true,
  overflow: false,
  transition: "el-fade-in"
}

const goto = (name: string) => {
  router.push({ name: name })
}

const asideStyle = computed(() => {
  return {
    // height: window.outerHeight + 'px'
    height: window.innerHeight + "px"
  }
})
</script>

<template>
<el-container class="layout-container-demo">
  <el-aside :style="asideStyle" class="glassmorphism">
    <el-scrollbar>
      <el-menu>
        <el-menu-item index="1" @click="goto('home')">
          <el-icon>
            <HomeFilled />
          </el-icon>
          <span>主页</span>
        </el-menu-item>
        <el-menu-item index="2">
          <el-icon><List /></el-icon>
          <span>点歌列表</span>
        </el-menu-item>
      </el-menu>
    </el-scrollbar>
  </el-aside>

  <el-container class="main-container">
    <el-header class="glassmorphism">
      <el-menu mode="horizontal" :ellipsis="false" class="toolbar">
        <el-menu-item index="0">
          <img src="/assets/images/logo.png" alt="logo" style="width:100px;" />
        </el-menu-item>
        <el-menu-item index="1">
          <el-icon>
            <StarFilled />
          </el-icon>
        </el-menu-item>
        <el-menu-item index="2">
          <el-icon>
            <Share />
          </el-icon>
        </el-menu-item>
      </el-menu>
    </el-header>

    <el-main>
      <el-config-provider :locale="zhCn" :card="cardConfig" :dialog="dialogConfig">
        <RouterView></RouterView>
        <el-backtop :right="100" :bottom="100" />
      </el-config-provider>
    </el-main>
  </el-container>
</el-container>
</template>

<style scoped>
.el-menu--horizontal>.el-menu-item:nth-child(1) {
  margin-right: auto;
}

.layout-container-demo {
  width: 100%;
  height: 100%;
}

.layout-container-demo .el-aside {
  color: var(--el-text-color-primary);
  box-shadow: 2px 0 2px rgba(0, 0, 0, 0.2);
  width: 200px;
  position: fixed;
  left: 0;
  top: 60px;
  right: 0;
  z-index: 100;
}

.layout-container-demo .el-header {
  position: fixed;
  width: 100%;
  left: 0;
  top: 0;
  right: 0;
  z-index: 100;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: var(--el-text-color-primary);
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
}

.layout-container-demo .el-menu {
  border-right: none;
}

.main-container .el-main {
  width: calc(100vw - 200px);
  left: 200px;
  top: 60px;
  position: absolute;
}

.layout-container-demo .toolbar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  width: 100%;
  right: 20px;
  background-color: transparent;
  text-align: right;
  font-size: 24px;
}
</style>
