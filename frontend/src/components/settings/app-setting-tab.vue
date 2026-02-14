<script setup lang="ts">
import { ElMessage, type FormInstance } from "element-plus"
import { Close, Check } from "@element-plus/icons-vue"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
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

const { data: globalConfigData, isFetching } = useGetGlobalConfig()


const globalConfigMutation = useMutation({
    mutationFn: async (params: GlobalConfigModel) => await addOrUpdateGlobalConfig({ data: params }),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "请求失败")
        } else {
            baseFormValue.id = response.data
            ElMessage.success(response.msg || "保存成功")
            toggleDark(baseFormValue.dark_mode)
            themeStore.setDarkTheme(baseFormValue.dark_mode)
        }
        btnLoading.value = false
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

const addOrUpdateConfig = () => {
    btnLoading.value = true
    globalConfigMutation.mutate(baseFormValue)
}

watchEffect(() => {
    const darkTheme = themeStore.getDarkTheme()
    baseFormValue.dark_mode = darkTheme
})

watch(isFetching, () => {
    if (globalConfigData && globalConfigData.value) {
        baseFormValue.id = globalConfigData.value.id
        baseFormValue.check_update = globalConfigData.value.check_update
        baseFormValue.collapse = globalConfigData.value.collapse
        baseFormValue.dark_mode = globalConfigData.value.dark_mode
        baseFormValue.navSideTour = globalConfigData.value.navSideTour
        baseFormValue.notification = globalConfigData.value.notification
        baseFormValue.startup = globalConfigData.value.startup
    }
})

</script>
<template>
    <el-card>
        <template #header>
            <div class="card-header">
                <span>应用设置</span>
            </div>
        </template>
        <el-form ref="refForm" v-loading="isFetching" :model="baseFormValue" label-width="auto" inline>
            <el-form-item label="黑暗模式" prop="dark_mode">
                <el-switch v-model="baseFormValue.dark_mode" inline-prompt style="--el-switch-off-color: #ff4949"
                    :active-icon="Check" :inactive-icon="Close"></el-switch>
            </el-form-item>
            <el-form-item label="桌面通知" prop="notification">
                <el-switch v-model="baseFormValue.notification" inline-prompt style="--el-switch-off-color: #ff4949"
                    :active-icon="Check" :inactive-icon="Close"></el-switch>
            </el-form-item>
            <el-form-item label="自动检查更新" prop="check_update">
                <el-switch v-model="baseFormValue.check_update" inline-prompt style="--el-switch-off-color: #ff4949"
                    :active-icon="Check" :inactive-icon="Close"></el-switch>
            </el-form-item>
            <el-form-item label="开机启动" prop="startup">
                <el-switch v-model="baseFormValue.startup" inline-prompt style="--el-switch-off-color: #ff4949"
                    :active-icon="Check" :inactive-icon="Close"></el-switch>
            </el-form-item>
            <el-form-item>
                <el-button v-loading="btnLoading" type="primary" @click="addOrUpdateConfig()">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
    <el-divider />
    <obs-setting />
</template>
