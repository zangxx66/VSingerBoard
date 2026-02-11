<script setup lang="tsx">
import { ElMessage, ElButton, type FormInstance } from 'element-plus'
import { request } from '@/api'

const refForm = ref<FormInstance>()
const baseFormValue = reactive<BiliConfigModel>({
    id: 0,
    room_id: 0,
    modal_level: 1,
    user_level: 0,
    sing_prefix: '点歌',
    sing_cd: 0,
})
const danmakuStore = useDanmakuStore()

const dropdownMenu = [
    {
        key: '普通用户',
        value: 0,
    },
    {
        key: '舰长',
        value: 3,
    },
    {
        key: '提督',
        value: 2,
    },
    {
        key: '总督',
        value: 1,
    },
]

const { data: biliConfigData, refetch, isFetching } = useGetBilibiliConfig()

const configMutation = useMutation({
    mutationFn: async (params: BiliConfigModel) => await request.addOrUpdateBiliConfig({ data: params }),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "请求失败")
        } else {
            ElMessage.success("操作成功")
            refetch()
            danmakuStore.clearDanmakuList("bilibili")
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
    if (typeof baseFormValue.modal_level != "number" || baseFormValue.modal_level < 0) {
        ElMessage.warning("请输入正确的粉丝牌等级")
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
    configMutation.mutate(baseFormValue)

}

watch(isFetching, () => {
    if (biliConfigData && biliConfigData.value) {
        baseFormValue.id = biliConfigData.value.id
        baseFormValue.room_id = biliConfigData.value.room_id
        baseFormValue.modal_level = biliConfigData.value.modal_level
        baseFormValue.user_level = biliConfigData.value.user_level
        baseFormValue.sing_prefix = biliConfigData.value.sing_prefix
        baseFormValue.sing_cd = biliConfigData.value.sing_cd
    }
})
</script>
<template>
    <el-card>
        <template #header>
            <div class="card-header">
                <span>基础设置</span>
            </div>
        </template>
        <el-form ref="refForm" v-loading="isFetching" :model="baseFormValue" label-width="auto">
            <el-form-item label="房间号" prop="room_id">
                <el-input-number v-model="baseFormValue.room_id" placeholder="B站直播间号" :min="1" :controls="false" />
            </el-form-item>
            <el-form-item label="粉丝牌等级" prop="modal_level">
                <el-input-number v-model="baseFormValue.modal_level" placeholder="粉丝牌等级" :min="0" :controls="false" />
            </el-form-item>
            <el-form-item label="用户等级" prop="user_level">
                <el-radio-group v-model="baseFormValue.user_level">
                    <template v-for="(item, index) in dropdownMenu" :key="index">
                        <el-radio :value="item.value">{{ item.key }}</el-radio>
                    </template>
                </el-radio-group>
            </el-form-item>
            <el-form-item label="点歌指令" prop="sing_prefix">
                <el-input v-model="baseFormValue.sing_prefix" placeholder="点歌指令" type="text" style="width: 240px;" />
            </el-form-item>
            <el-form-item label="点歌cd" prop="sing_cd">
                <el-input-number v-model="baseFormValue.sing_cd" placeholder="点歌cd，单位：秒" :min="0" :controls="false" />
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="addOrUpdateConfig()">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
    <el-divider />
    <bili-credential />
</template>
