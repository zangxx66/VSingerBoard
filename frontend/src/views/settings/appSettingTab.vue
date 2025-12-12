<script setup lang="ts">
import { ElMessage, type FormInstance } from "element-plus"
import { Close, Check } from "@element-plus/icons-vue"
import { request } from "@/api"
import { toggleDark } from "@/utils"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
const loading = ref(false)
const themeStore = useThemeStore()
const baseFormValue = reactive<GlobalConfigModel>({
    id: 0,
    dark_mode: false,
    check_update: false,
    startup: false,
    notification: false,
    navSideTour: false,
    collapse: false
})

const initConfig = () => {
    loading.value = true
    request
    .getGlobalConfig({})
    .then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0){
            ElMessage.warning(resp.msg || "获取失败")
        }else{
            const data = resp.data.data
            if(data){
                Object.assign(baseFormValue, data)
            }
        }
        loading.value = false
    })
    .catch(error => {
        ElMessage.error(error)
        console.error("getGlobalConfig", error)
        loading.value = false
    })
}

const addOrUpdateConfig = () => {
    btnLoading.value = true
    request
    .addOrUpdateGlobalConfig({ data: baseFormValue })
    .then(response => {
        const resp = response.data as ResponseModel
        if(resp.code != 0){
            ElMessage.warning(resp.msg || "保存失败")
        }else{
            baseFormValue.id = resp.data
            ElMessage.success(resp.msg || "保存成功")
            toggleDark(baseFormValue.dark_mode)
            themeStore.setDarkTheme(baseFormValue.dark_mode)
        }
        btnLoading.value = false
    })
    .catch(error => {
        console.log(error)
        ElMessage.error(error)
        btnLoading.value = false
    })
}

watchEffect(() => {
    const darkTheme = themeStore.getDarkTheme()
    baseFormValue.dark_mode = darkTheme
})

defineExpose({ initConfig })
</script>
<template>
    <el-card v-loading="loading">
        <template #header>
            <div class="card-header">
                <span>应用设置</span>
            </div>
        </template>
        <el-form :model="baseFormValue" ref="refForm" label-width="auto" inline>
            <el-form-item label="黑暗模式" prop="dark_mode">
                <el-switch 
                v-model="baseFormValue.dark_mode"
                inline-prompt
                style="--el-switch-off-color: #ff4949"
                :active-icon="Check"
                :inactive-icon="Close"
                ></el-switch>
            </el-form-item>
            <el-form-item label="桌面通知" prop="notification">
                <el-switch 
                v-model="baseFormValue.notification"
                inline-prompt
                style="--el-switch-off-color: #ff4949"
                :active-icon="Check"
                :inactive-icon="Close"  
                ></el-switch>
            </el-form-item>
            <el-form-item label="自动检查更新" prop="check_update">
                <el-switch 
                v-model="baseFormValue.check_update"
                inline-prompt
                style="--el-switch-off-color: #ff4949"
                :active-icon="Check"
                :inactive-icon="Close"
                ></el-switch>
            </el-form-item>
            <el-form-item label="开机启动" prop="startup">
                <el-switch 
                v-model="baseFormValue.startup"
                inline-prompt
                style="--el-switch-off-color: #ff4949"  
                :active-icon="Check"
                :inactive-icon="Close"
                ></el-switch>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="addOrUpdateConfig()" v-loading="btnLoading">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
    <el-divider />
    <obs-setting />
</template>
