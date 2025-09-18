<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue"

const activeName = ref("1")
const biliTab = defineAsyncComponent(() => import("./biliTab.vue"))
const dyTab = defineAsyncComponent(() => import("./dyTab.vue"))
</script>
<template>
  <el-container class="home-container">
    <el-main class="home-main">
      <el-tabs v-model="activeName" type="border-card" class="demo-tabs">
        <el-tab-pane label="bilibili设置" name="1">
          <bili-tab></bili-tab>
        </el-tab-pane>
        <el-tab-pane label="抖音设置" name="2" lazy>
          <dy-tab></dy-tab>
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>
<style scoped>
.home-container {
  height: calc(100vh - 60px);
}
</style>