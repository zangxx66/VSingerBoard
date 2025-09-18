<script setup lang="ts">
import { defineAsyncComponent } from "vue"

const BiliChat = defineAsyncComponent(() => import("@/components/room/chat.vue"))
const Settings = defineAsyncComponent(() => import("@/components/home/setting.vue"))
</script>
<template>
    <el-container class="room-container">
        <el-main class="room-main">
            <el-splitter>
                <el-splitter-panel min="30%">
                    <bili-chat></bili-chat>
                </el-splitter-panel>
                <el-splitter-panel min="30%">
                    <settings></settings>
                </el-splitter-panel>
            </el-splitter>
        </el-main>
    </el-container>
</template>