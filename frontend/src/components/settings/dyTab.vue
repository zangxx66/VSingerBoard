<script setup lang="ts">
import { ElMessage, type FormInstance } from "element-plus"
import { request } from "@/api"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
const loading = ref(false)
const baseFormValue = reactive<DyConfigModel>({
    id: 0,
    room_id: 0,
    sing_prefix: '点歌',
    sing_cd: 0,
    fans_level: 1
})
const danmakuStore = useDanmakuStore()

const initConfig = () => {
    loading.value = true
    request.getDyConfig({}).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            if (!resp.data.data) {
                loading.value = false
                return
            }
            Object.assign(baseFormValue, resp.data.data)
        }
        loading.value = false
    }).catch(error => {
        ElMessage.error(error)
        loading.value = false
    })
}

const addOrUpdateConfig = () => {
    if (typeof baseFormValue.room_id != "number" || baseFormValue.room_id < 1) {
        ElMessage.warning("请输入正确的房间号")
        return
    }
    if (baseFormValue.sing_prefix.length == 0) {
        ElMessage.warning("请输入正确的点歌指令")
        return
    }
    if (typeof baseFormValue.sing_cd != "number" || baseFormValue.sing_cd < 0) {
        ElMessage.warning("请输入正确的点歌cd")
        return
    }
    if (typeof baseFormValue.fans_level != "number" || baseFormValue.fans_level < 0) {
        ElMessage.warning("请输入正确的粉团等级")
        return
    }
    btnLoading.value = true
    request.addOrUpdateDyConfig({ data: baseFormValue }).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            ElMessage.success(resp.msg)
            baseFormValue.id = resp.data
            danmakuStore.clearDanmakuList()
        }
        btnLoading.value = false
    }).catch(error => {
        ElMessage.error(error)
        btnLoading.value = false
    })
}


onMounted(() => {
    initConfig()
})
</script>
<template>
    <el-card>
        <template #header>
            <div class="card-header">
                <span>抖音设置</span>
            </div>
        </template>
        <el-form :mode="baseFormValue" ref="refForm" label-width="auto" v-loading="loading">
            <el-form-item label="房间号" prop="room_id">
                <el-input-number v-model="baseFormValue.room_id" :min="1" :controls="false" />
            </el-form-item>
            <el-form-item label="点歌指令" prop="sing_prefix">
                <el-input v-model="baseFormValue.sing_prefix" type="text" style="width: 240px;" />
            </el-form-item>
            <el-form-item label="点歌cd" prop="sing_cd">
                <el-input-number v-model="baseFormValue.sing_cd" placeholder="点歌cd，单位：秒" :min="0" :controls="false" />
            </el-form-item>
            <el-form-item label="粉团等级" prop="fans_level">
                <el-input-number v-model="baseFormValue.fans_level" :min="0" :controls="false" />
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="addOrUpdateConfig" v-loading="btnLoading">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
</template>
