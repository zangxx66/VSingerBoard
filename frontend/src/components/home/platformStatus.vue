<script setup lang="ts">
import { computed, ref } from 'vue'
import { CircleCheckFilled, CircleCloseFilled, WarnTriangleFilled } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"

const props = defineProps<{
    platform: 'douyin' | 'bilibili'
    roomId: number
    wsStatus: number
}>()

const loading = ref(false)
const refreshStatus = () => {
    loading.value = true
    try {
        if(props.platform == "bilibili") {
            window.pywebview.api.restart_bilibili_ws()
        } else {
            window.pywebview.api.restart_douyin_ws()
        }
        ElMessage.success("刷新成功，请等待操作完成")
    } catch (error: any) {
        ElMessage.error(error)
    } finally {
        setTimeout(() => {
            loading.value = false
        }, 5000)
    }
}

const wsStatusMap = {
    bilibili: new Map<number, any>([
        [-1, { color: '#F56C6C', icon: CircleCloseFilled, message: "未配置或出现错误" }],
        [0, { color: '#E6A23C', icon: WarnTriangleFilled, message: "初始化" }],
        [1, { color: '#E6A23C', icon: WarnTriangleFilled, message: "连接建立中" }],
        [2, { color: '#67C23A', icon: CircleCheckFilled, message: "已连接" }],
        [3, { color: '#E6A23C', icon: WarnTriangleFilled, message: "断开连接中" }],
        [4, { color: '#F56C6C', icon: CircleCloseFilled, message: "已断开" }],
        [5, { color: '#F56C6C', icon: CircleCloseFilled, message: "出现错误" }]
    ]),
    douyin: new Map<number, any>([
        [-1, { color: '#F56C6C', icon: CircleCloseFilled, message: "未配置或出现错误" }],
        [0, { color: '#E6A23C', icon: WarnTriangleFilled, message: "未连接" }],
        [1,  { color: '#67C23A', icon: CircleCheckFilled, message: "已连接" }],
        [2, { color: '#E6A23C', icon: WarnTriangleFilled, message: "已断开" }],
        [3, { color: '#F56C6C', icon: CircleCloseFilled, message: "出现错误" }]
    ])
}

const wsState = computed(() => {
    return wsStatusMap[props.platform].get(props.wsStatus)
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