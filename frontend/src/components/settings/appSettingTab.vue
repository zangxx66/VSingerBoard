<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { ElMessage, type FormInstance } from "element-plus"
import { Close, Check } from "@element-plus/icons-vue"
import { request } from "@/api"
import { toggleDark, checkUpdate } from "@/utils"
import { useIntervalStore, useThemeStore } from "@/stores"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
const intervalStore = useIntervalStore()
const themeStore = useThemeStore()
const baseFormValue = reactive<GlobalConfigModel>({
    id: 0,
    dark_mode: false,
    check_update: false,
    startup: false
})

const initConfig = () => {
    request
    .getGlobalConfig({})
    .then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0){
            ElMessage.warning(resp.msg || "获取失败")
        }else{
            const data = resp.data.data
            if(data){
                const model = data as GlobalConfigModel
                baseFormValue.id = model.id
                baseFormValue.dark_mode = model.dark_mode
                baseFormValue.check_update = model.check_update
                baseFormValue.startup = model.startup
            }
        }
    })
    .catch(error => {
        ElMessage.error(error)
        console.error("getGlobalConfig", error)
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
            ElMessage.success(resp.msg || "保存成功")
            toggleDark(baseFormValue.dark_mode)
            themeStore.setDarkTheme(baseFormValue.id, baseFormValue.dark_mode)
            if(baseFormValue.check_update){
                intervalStore.addInterval("check_update", checkUpdate, 1000 * 60 * 60 * 6)
            }else{
                intervalStore.removeInterval("check_update")
            }
            initConfig()
        }
        btnLoading.value = false
    })
    .catch(error => {
        ElMessage.error(error)
        btnLoading.value = false
    })
}

// onMounted(() => {
//     initConfig()
// })
defineExpose({ initConfig })
</script>
<template>
    <el-card>
        <template #header>
            <div class="card-header">
                <span>应用设置</span>
            </div>
        </template>
        <el-form :model="baseFormValue" ref="refForm" label-width="auto">
            <el-form-item label="黑暗模式" prop="dark_mode">
                <el-switch 
                v-model="baseFormValue.dark_mode"
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
                :model-value="baseFormValue.startup"
                inline-prompt
                style="--el-switch-off-color: #ff4949"  
                active-text="开"
                inactiveText="关"
                ></el-switch>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="addOrUpdateConfig()" v-loading="btnLoading">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
</template>
