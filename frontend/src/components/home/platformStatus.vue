<script setup lang="ts">
import { computed, ref } from 'vue'
import { CircleCheckFilled, CircleCloseFilled, WarnTriangleFilled } from "@element-plus/icons-vue"

const props = defineProps<{
    platform: 'douyin' | 'bilibili'
    roomId: number
    wsStatus: number
}>()

const loading = ref(false)
const refreshStatus = () => {
    loading.value = true
    if(props.platform == "bilibili") {
        window.pywebview.api.restart_bilibili()
    }
    else{
        window.pywebview.api.restart_douyin()
    }
    setTimeout(() => {
        loading.value = false
    }, 5000)
}

const wsState = computed(() => {
    if (props.platform == "bilibili") {
        if (props.wsStatus >= 0 && props.wsStatus <= 2) {
            return { color: '#67C23A', icon: CircleCheckFilled, message: "已连接" }
        }
        else if (props.wsStatus == -1) {
            return { color: '#E6A23C', icon: CircleCloseFilled, message: "未配置或出现错误" }
        }
        else {
            return { color: '#F56C6C', icon: WarnTriangleFilled, message: "已断开" }
        }
    }
    else {
        if (props.wsStatus == 1) {
            return { color: '#67C23A', icon: CircleCheckFilled, message: "已连接" }
        }
        else if (props.wsStatus == 0) {
            return { color: '#E6A23C', icon: WarnTriangleFilled, message: "已断开" }
        }
        else {
            return { color: '#F56C6C', icon: CircleCloseFilled, message: "未配置或出现错误" }
        }
    }
})
</script>
<template>
    <div class="platform-status-container">
        <img :src="`/assets/images/${platform}.png`" class="source-img" :alt="platform" width="24" />：{{ roomId }}
        &nbsp;
        <el-tooltip placement="top">
            <template #content>
                <span>当前状态：{{ wsState.message }}，如有异常点击重新连接</span>
            </template>
            <el-button text @click="refreshStatus" v-loading="loading">
                <el-icon :color="wsState.color" class="status-img">
                    <component :is="wsState.icon" />
                </el-icon>
            </el-button>
        </el-tooltip>
    </div>
</template>
<style scoped>
.platform-status-container {
    display: flex;
    align-items: center;
}

.source-img {
    margin: 1px;
    height: 24px;
}
</style>