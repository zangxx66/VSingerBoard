<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue"

const activeName = ref("1")
const biliTab = defineAsyncComponent(() => import("./biliTab.vue"))
</script>
<template>
  <el-container class="home-container">
    <el-main class="home-main">
      <el-card class="home-tab-card">
        <el-tabs v-model="activeName" type="border-card" class="demo-tabs">
          <el-tab-pane label="bilibili设置" name="1">
            <bili-tab></bili-tab>
          </el-tab-pane>
          <el-tab-pane label="抖音设置" name="2" lazy disabled> 抖音设置 </el-tab-pane>
        </el-tabs>
      </el-card>
    </el-main>
  </el-container>
</template>

