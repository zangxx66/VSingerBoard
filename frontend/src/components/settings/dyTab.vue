<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { ElMessage, ElNotification, type FormInstance } from "element-plus"
import { request } from "@/api"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
const baseFormValue = reactive<DyConfigModel>({
    id: 0,
    room_id: 0,
    sing_prefix: '点歌',
    sing_cd: 0
})

const initConfig = () => {
    request.getDyConfig({}).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            if(!resp.data.data)return
            const cfg = resp.data.data as DyConfigModel
            baseFormValue.id = cfg.id
            baseFormValue.room_id = cfg.room_id
            baseFormValue.sing_prefix = cfg.sing_prefix
            baseFormValue.sing_cd = cfg.sing_cd
        }
    }).catch(error => ElMessage.error(error))
}

const addOrUpdateConfig = () => {
    btnLoading.value = true
    request.addOrUpdateDyConfig({ data: baseFormValue }).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        }else{
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
    else if (dy_ws == 1) {
        dy_msg = "抖音已重新连接"
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
        <el-form :mode="baseFormValue" ref="refForm" label-width="auto">
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
