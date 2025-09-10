<script setup lang="ts">
import { ref, defineAsyncComponent } from "vue"

const BiliChat = defineAsyncComponent(() => import("@/components/room/biliChat.vue"))
</script>
<template>
    <el-container class="room-container">
        <el-main class="room-main">
            <el-splitter>
                <el-splitter-panel min="30%">
                    <bili-chat></bili-chat>
                </el-splitter-panel>
                <el-splitter-panel min="30%">

                </el-splitter-panel>
            </el-splitter>
        </el-main>
    </el-container>
</template>
<style scoped>
.room-watermark {
    height: calc(100vh - 80px);
    overflow: hidden;
}
</style>