<script setup lang="tsx">
import { ref, reactive, onMounted, defineAsyncComponent } from 'vue'
import { ElMessage, ElButton, type FormInstance } from 'element-plus'
import { request } from '@/api'
import { useDanmakuStore } from "@/stores"

const biliCredential = defineAsyncComponent(() => import("./biliCredential.vue"))
const refForm = ref<FormInstance>()
const loading = ref(false)
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

const initConfig = () => {
    loading.value = true
    request
        .getBiliConfig({})
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg)
            } else {
                const data = resp.data.data
                if (data) {
                    Object.assign(baseFormValue, data)
                }
            }
            loading.value = false
        })
        .catch((error) => {
            ElMessage.error(error)
            console.error("getBiliConfig", error)
            loading.value = false
        })
}

const addOrUpdateConfig = () => {
    if(typeof baseFormValue.room_id != "number" || baseFormValue.room_id < 1) {
        ElMessage.warning("请输入正确的房间号")
        return
    }
    if(typeof baseFormValue.modal_level != "number" || baseFormValue.modal_level < 0) {
        ElMessage.warning("请输入正确的粉丝牌等级")
        return
    }
    if(baseFormValue.sing_prefix.length == 0) {
        ElMessage.warning("请输入正确的点歌指令")
        return
    }
    if(typeof baseFormValue.sing_cd != "number" || baseFormValue.sing_cd < 0) {
        ElMessage.warning("请输入正确的点歌cd")
        return
    }
    request
        .addOrUpdateBiliConfig({ data: baseFormValue })
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg)
            } else {
                ElMessage.success(resp.msg)
                baseFormValue.id = resp.data
                danmakuStore.clearDanmakuList()
            }
        })
        .catch((error) => ElMessage.error(error))

}

onMounted(() => {
    initConfig()
})
</script>
<template>
    <div v-loading="loading">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>基础设置</span>
                </div>
            </template>
            <el-form :model="baseFormValue" ref="refForm" label-width="auto">
                <el-form-item label="房间号" prop="room_id">
                    <el-input v-model="baseFormValue.room_id" placeholder="B站直播间号" type="text" min="1" />
                </el-form-item>
                <el-form-item label="粉丝牌等级" prop="modal_level">
                <el-input v-model="baseFormValue.modal_level" placeholder="粉丝牌等级" type="text" min="0" />
            </el-form-item>
            <el-form-item label="用户等级" prop="user_level">
                <el-radio-group v-model="baseFormValue.user_level">
                    <template v-for="item in dropdownMenu">
                        <el-radio :value="item.value">{{ item.key }}</el-radio>
                    </template>
                </el-radio-group>
            </el-form-item>
                <el-form-item label="点歌指令" prop="sing_prefix">
                    <el-input v-model="baseFormValue.sing_prefix" placeholder="点歌指令" type="text" />
                </el-form-item>
                <el-form-item label="点歌cd" prop="sing_cd">
                <el-input v-model="baseFormValue.sing_cd" placeholder="点歌cd，单位：秒" type="text" min="0" />
            </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="addOrUpdateConfig()">保存</el-button>
                </el-form-item>
            </el-form>
        </el-card>
        <el-divider />
        <bili-credential></bili-credential>
    </div>
</template>
