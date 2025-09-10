<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent, computed } from "vue"
import { RouterView } from "vue-router"
import zhCn from "element-plus/es/locale/lang/zh-cn"
import { Setting, StarFilled } from "@element-plus/icons-vue"
import { ContextMenu } from '@imengyu/vue3-context-menu'
import { ElMessage } from "element-plus"

const cardConfig = {
  shadow: "always"
}

const dialogConfig = {
  alignCenter: true,
  draggable: true,
  overflow: false,
  transition: "el-fade-in"
}

const show = ref(false)
const options = ref({
  zIndex: 100,
  minWidth: 230,
  x: 500,
  y: 200,
  theme: "mac"
})
function onContextMenu(e: MouseEvent) {
  e.preventDefault()
  show.value = true
  options.value.x = e.x
  options.value.y = e.y
}

const refresh = () => console.log("refresh")
const isSelection = computed(() => {
  const selectText = window.getSelection()?.toString()
  if(selectText)return true
  return false
})
async function copyToClipboard() {
  const selectText = window.getSelection()?.toString()
  if (selectText) {
    await navigator.clipboard.writeText(selectText)
    ElMessage.success("复制成功")
  }
}

onMounted(() => {
  const dom = document.querySelector(".layout-container-demo .el-main") as HTMLElement
  dom.style.width = window.innerWidth + "px"
})

const isShow = ref(false)
const settingComponent = defineAsyncComponent(() => import("@/components/home/setting.vue"))
</script>

<template>
  <el-container class="layout-container-demo" @contextmenu="onContextMenu($event)">
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
        <el-menu-item index="2" @click="isShow = true">
          <el-icon>
            <Setting />
          </el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
    </el-header>

    <el-main>
      <el-config-provider :locale="zhCn" :card="cardConfig" :dialog="dialogConfig">
        <RouterView></RouterView>
        <el-backtop :right="100" :bottom="100" />
      </el-config-provider>
    </el-main>
    <el-drawer v-model="isShow" direction="rtl" resizable destroy-on-close>
      <template #header>
        <el-text>
          <el-icon>
            <Setting />
          </el-icon>
          设置
        </el-text>
      </template>
      <template #default>
        <setting-component></setting-component>
      </template>
    </el-drawer>
    <context-menu v-model:show="show" :options="options">
      <context-menu-item label="重新加载" @click="refresh"  />
      <context-menu-item v-if="isSelection" label="复制" @click="copyToClipboard" />
    </context-menu>
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

.layout-container-demo .el-main {
  height: calc(100vh - 60px);
  left: 0;
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
