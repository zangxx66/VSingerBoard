<script setup lang="ts">
import type { TabsPaneContext } from "element-plus"

defineOptions({
  name: "settings"
})

const activeName = ref("1")

const appSettingRef = useTemplateRef("appSettingRef")
const tabClickHandle = (pane: TabsPaneContext, ev: Event) => {
  
}

</script>
<template>
  <el-container class="settings-container">
    <el-main class="settings-main">
      <el-tabs v-model="activeName" type="border-card" class="settings-tabs" @tab-click="tabClickHandle">
        <el-tab-pane label="哔哩哔哩设置" name="1">
          <bili-tab />
        </el-tab-pane>
        <el-tab-pane label="抖音设置" name="2" lazy>
          <dy-tab />
        </el-tab-pane>
        <el-tab-pane label="应用设置" name="3">
          <app-setting-tab ref="appSettingRef" />
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>
