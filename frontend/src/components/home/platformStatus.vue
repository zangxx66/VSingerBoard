<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheckFilled, CircleCloseFilled, WarnTriangleFilled } from "@element-plus/icons-vue"

const props = defineProps<{
    platform: 'douyin' | 'bilibili'
    roomId: number
    wsStatus: number
}>()

const wsState = computed(() => {
    if(props.platform == "bilibili"){
        if(props.wsStatus >= 0 && props.wsStatus <=2){
            return { color: '#67C23A', icon: CircleCheckFilled }
        }
        else if(props.wsStatus == -1){
            return { color: '#E6A23C', icon: WarnTriangleFilled }
        }
        else{
            return { color: '#F56C6C', icon: CircleCloseFilled }
        }
    }
    else{
        if(props.wsStatus == 1){
            return { color: '#67C23A', icon: CircleCheckFilled }
        }
        else if(props.wsStatus == -1){
            return { color: '#E6A23C', icon: WarnTriangleFilled }
        }
        else{
            return { color: '#F56C6C', icon: CircleCloseFilled }
        }
    }
})
</script>
<template>
    <img :src="`/assets/images/${platform}.png`" class="source-img" :alt="platform" width="24" />：{{ roomId }}
    &nbsp;
    <el-icon :color="wsState.color" class="source-img">
        <component :is="wsState.icon" />
    </el-icon>
</template>
<style scoped>
.source-img {
    margin: 1px;
    height: 24px;
}
</style>