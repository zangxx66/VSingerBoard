<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { ElMessage, ElNotification, type FormInstance } from "element-plus"
import { request } from "@/api"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
const loading = ref(false)
const baseFormValue = reactive<DyConfigModel>({
    id: 0,
    room_id: 0,
    sing_prefix: '点歌',
    sing_cd: 0
})

const initConfig = () => {
    loading.value = true
    request.getDyConfig({}).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            if(!resp.data.data){
                loading.value = false
                return
            }
            const cfg = resp.data.data as DyConfigModel
            Object.assign(baseFormValue, cfg)
        }
        loading.value = false
    }).catch(error => {
        ElMessage.error(error)
        loading.value = false
    })
}

const addOrUpdateConfig = () => {
    btnLoading.value = true
    request.addOrUpdateDyConfig({ data: baseFormValue }).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        }else{
            window.pywebview.api.restart_douyin_ws()
            ElMessage.success(resp.msg)
            initConfig()
            setTimeout(() => {
                checkWsStatus()
            }, 1000)
        }
        btnLoading.value = false
    }).catch(error => {
        ElMessage.error(error)
        btnLoading.value = false
    })
}

const checkWsStatus = async() => {
    const dy_ws: number = await window.pywebview.api.get_dy_ws_status()
    let dy_msg = ""
    if (dy_ws == -1) {
        dy_msg = "抖音未配置"
    }
    else if (dy_ws == 0){
        dy_msg = "抖音未连接"
    }
    else if (dy_ws == 1) {
        dy_msg = "抖音已重新连接"
    }
    else if (dy_ws == 2) {
        dy_msg = "抖音连接已断开"
    }
    else {
        dy_msg = "抖音连接发生错误"
    }
    ElNotification({
        title: "提示",
        message: dy_msg,
        type: dy_ws > 0 ? "success" : "warning",
        position: "bottom-right"
    })
}

onMounted(() => {
    initConfig()
})
</script>
<template>
    <el-card>
        <el-form :mode="baseFormValue" ref="refForm" label-width="auto" v-loading="loading">
            <el-form-item label="房间号" prop="room_id">
                <el-input v-model="baseFormValue.room_id" type="text" min="1" />
            </el-form-item>
            <el-form-item label="点歌指令" prop="sing_prefix">
                <el-input v-model="baseFormValue.sing_prefix" type="text" />
            </el-form-item>
            <!-- <el-form-item label="点歌cd" prop="sing_cd">
                <el-input v-model="baseFormValue.sing_cd" type="text" min="0" />
            </el-form-item> -->
            <el-form-item>
                <el-button type="primary" @click="addOrUpdateConfig" v-loading="btnLoading">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
</template>
