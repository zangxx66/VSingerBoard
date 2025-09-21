<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { ElMessage, type FormInstance } from "element-plus"
import { request } from "@/api"
import type { ResponseModel, GlobalConfigModel } from "@/types"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
const version = ref("")
const baseFormValue = reactive<GlobalConfigModel>({
    id: 0,
    dark_mode: false,
    check_update: false,
    startup: false
})

const getVersion = async() =>{
    // @ts-ignore
    version.value = await window.pywebview.api.get_version()
} 

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
            initConfig()
        }
        btnLoading.value = false
    })
    .catch(error => {
        ElMessage.error(error)
        btnLoading.value = false
    })
}

const openGithub = () => {
    const a = document.createElement("a")
    a.href = "https://github.com/zangxx66/VSingerBoard"
    a.target = "_blank"
    a.click()
}

const openHomepage = () => {
    const a = document.createElement("a")
    a.href = "https://space.bilibili.com/909267"
    a.target = "_blank"
    a.click()
}

const openIssues = () => {
    const a = document.createElement("a")
    a.href = "https://github.com/zangxx66/VSingerBoard/issues"
    a.target = "_blank"
    a.click()
}

onMounted(() => {
    getVersion()
    initConfig()
})
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
                :model-value="baseFormValue.dark_mode"
                inline-prompt
                style="--el-switch-off-color: #ff4949"
                active-text="开"
                inactiveText="关"
                ></el-switch>
            </el-form-item>
            <el-form-item label="自动检查更新" prop="check_update">
                <el-switch 
                :model-value="baseFormValue.check_update"
                inline-prompt
                style="--el-switch-off-color: #ff4949"
                active-text="开"
                inactiveText="关"
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
    <el-divider />
    <el-card>
        <template #header>
            <div class="card-header">
                <span>关于</span>
            </div>
        </template>
        <div class="about-container">
            <img src="/assets/images/logo.png" alt="logo" class="about-logo" width="70" />
            <div class="about-title">点歌姬</div>
            <div class="about-version">v{{ version }}</div>
            <div class="about-author-container">
                <el-button color="#909399" @click="openGithub" plain>GitHub仓库</el-button>
                <el-button color="#F56C6C" @click="openHomepage" plain>作者主页</el-button>
                <el-button color="#67C23A" @click="openIssues" plain>问题反馈</el-button>
            </div>
        </div>
    </el-card>
</template>
<style scoped>
.about-container {
    position: relative;
    display: block;
}

.about-logo {
    margin: 0 auto;
    display: block;
    width: 200px;
    height: 100px;
}

.about-title {
    margin: 0 auto;
    display: block;
    text-align: center;
    width: 200px;
    height: 20px;
    font-size: x-large;
}

.about-version {
    margin: 0 auto;
    margin-top: 3%;
    display: block;
    text-align: center;
    width: 200px;
    height: 20px;
}

.about-author-container {
    margin: 0 auto;
    margin-top: 3%;
    display: flex;
    justify-content: center;
}
</style>