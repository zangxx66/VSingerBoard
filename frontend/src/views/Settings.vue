<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue"
import type { TabsPaneContext } from "element-plus"

const activeName = ref("1")
const biliTab = defineAsyncComponent(() => import("@/components/settings/biliTab.vue"))
const dyTab = defineAsyncComponent(() => import("@/components/settings/dyTab.vue"))
const appSetting = defineAsyncComponent(() => import("@/components/settings/appSettingTab.vue"))

const appSettingRef = ref<any>()
const tabClickHandle = (pane: TabsPaneContext, ev: Event) => {
  if(pane.props.name == 3){
    appSettingRef.value.initConfig()
  }
}

</script>
<template>
  <el-container class="settings-container">
    <el-main class="settings-main">
      <el-tabs v-model="activeName" type="border-card" class="settings-tabs" @tab-click="tabClickHandle">
        <el-tab-pane label="哔哩哔哩设置" name="1">
          <bili-tab></bili-tab>
        </el-tab-pane>
        <el-tab-pane label="抖音设置" name="2" lazy>
          <dy-tab></dy-tab>
        </el-tab-pane>
        <el-tab-pane label="应用设置" name="3">
          <app-setting ref="appSettingRef"></app-setting>
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>
