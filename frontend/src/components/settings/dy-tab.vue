<script setup lang="ts">
import { ElMessage, type FormInstance } from "element-plus"
import { request } from "@/api"

const refForm = ref<FormInstance>()
const btnLoading = ref(false)
const baseFormValue = reactive<DyConfigModel>({
    id: 0,
    room_id: 0,
    sing_prefix: '点歌',
    sing_cd: 0,
    fans_level: 1
})
const danmakuStore = useDanmakuStore()

const { data: dyConfigData, refetch, isFetching } = useGetDouyinConfig()

const configMutation = useMutation({
    mutationFn: async (params: DyConfigModel) => await request.addOrUpdateDyConfig({ data: params }),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "请求失败")
        } else {
            ElMessage.success("操作成功")
            refetch()
            danmakuStore.clearDanmakuList("douyin")
            btnLoading.value = false
        }
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

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
    configMutation.mutate(baseFormValue)
}


watch(isFetching, () => {
    if(dyConfigData && dyConfigData.value) {
        baseFormValue.id = dyConfigData.value.id
        baseFormValue.room_id = dyConfigData.value.room_id
        baseFormValue.sing_prefix = dyConfigData.value.sing_prefix
        baseFormValue.sing_cd = dyConfigData.value.sing_cd
        baseFormValue.fans_level = dyConfigData.value.fans_level
    }
})
</script>
<template>
    <el-card>
        <template #header>
            <div class="card-header">
                <span>抖音设置</span>
            </div>
        </template>
        <el-form ref="refForm" v-loading="isFetching" :mode="baseFormValue" label-width="auto">
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
                <el-button v-loading="btnLoading" type="primary" @click="addOrUpdateConfig">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
</template>
