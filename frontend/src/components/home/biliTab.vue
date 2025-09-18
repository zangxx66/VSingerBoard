<script setup lang="tsx">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElText, ElButton, ElSwitch, type Column, type FormInstance } from 'element-plus'
import { Delete, Refresh } from '@element-plus/icons-vue'
import { request } from '@/api'
import type { ResponseModel, BiliConfigModel, BiliCredentialModel } from '@/types'

const refForm = ref<FormInstance>()
const isShow = ref(false)
const btnLoading = ref(false)
const timer = ref(0)
const qrCode = ref('')
const qrCodeText = ref('')
const credentialList = ref(Array<BiliCredentialModel>())
const baseFormValue = reactive<BiliConfigModel>({
    id: 0,
    room_id: 0,
    modal_level: 0,
    user_level: 0,
    sing_prefix: '点歌',
    sing_cd: 0,
})

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
const credentialColumns: Column<any>[] = [
    {
        key: 'uid',
        dataKey: 'uid',
        title: 'uid',
        width: 100,
        cellRenderer: ({ cellData: uid }) => <ElText>{uid} </ElText>,
    },
    {
        key: 'uname',
        dataKey: 'uname',
        title: '昵称',
        width: 250,
        cellRenderer: ({ cellData: uname }) => <ElText>{uname} </ElText>,
    },
    {
        key: 'enable',
        dataKey: 'enable',
        title: '是否启用',
        width: 150,
        cellRenderer: ({ rowData }) => (
            <ElSwitch
                modelValue={rowData.enable}
                inline-prompt
                style="--el-switch-off-color: #ff4949"
                activeText="启用"
                inactiveText="禁用"
                onChange={(val: string | number | boolean) => {
                    rowData.enable = val
                    changeStatus(val, rowData.id)
                }}
            >
                {' '}
            </ElSwitch>
        ),
    },
    {
        key: 'operations',
        title: '操作',
        width: 100,
        cellRenderer: ({ rowData }) => (
            <>
                <ElButton
                    type="primary"
                    icon={Refresh}
                    loading={btnLoading.value}
                    onClick={(evt: MouseEvent) => refreshSub(rowData.id)}
                >
                    刷新
                </ElButton>
                <ElButton
                    type="danger"
                    icon={Delete}
                    onClick={(evt: MouseEvent) => removeSub(rowData.id)}
                >
                    删除
                </ElButton>
            </>
        ),
    },
]

const initConfig = () => {
    request
        .getBiliConfig({})
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg)
            } else {
                const data = resp.data.data
                if (data) {
                    const model = data as BiliConfigModel
                    baseFormValue.id = model.id
                    baseFormValue.room_id = model.room_id
                    baseFormValue.modal_level = model.modal_level
                    baseFormValue.user_level = model.user_level
                    baseFormValue.sing_prefix = model.sing_prefix
                    baseFormValue.sing_cd = model.sing_cd
                }
            }
        })
        .catch((error) => ElMessage.error(error))
}

const initCredential = () => {
    request.getBiliCredntialList({}).then((response) => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            credentialList.value = resp.data.rows
        }
    })
}

const addOrUpdateConfig = () => {
    request
        .addOrUpdateBiliConfig({ data: baseFormValue })
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg)
            } else {
                ElMessage.success(resp.msg)
                initConfig()
            }
        })
        .catch((error) => ElMessage.error(error))
    
}

const changeStatus = (val: string | number | boolean, id: number) => {
    credentialList.value.forEach((value, index, array) => {
        if (value.id == id) return
        value.enable = !val
    })
}

const addSub = () => {
    request
        .getBiliCredentialCode({})
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg)
                return
            }
            qrCode.value = resp.data.data
            timer.value = setInterval(checkQrCode, 1000)
            isShow.value = true
        })
        .catch((error) => ElMessage.error(error))
}

const removeSub = (id: number) => {
    ElMessageBox.confirm('是否删除？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
        .then(() => request.deleteBiliCredential({ id: id }))
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg)
            } else {
                ElMessage.success(resp.msg)
                const list = credentialList.value.filter((item) => item.id != id)
                credentialList.value = list
            }
        })
        .catch((error) => {
            if ('string' == typeof error && 'cancel' == error) return
            ElMessage.error(error)
        })
}

const refreshSub = (id: number) => {
    btnLoading.value = true
    request
        .refreshBiliCredential({ id: id })
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg)
            } else {
                ElMessage.success('success')
            }
            btnLoading.value = false
        })
        .catch((error) => {
            ElMessage.error(error)
            btnLoading.value = false
        })
}

const checkQrCode = () => {
    request
        .checkQrCode({})
        .then((response) => {
            const resp = response.data as ResponseModel
            if (resp.code == 0) {
                if (resp.msg == 'success') {
                    clearInterval(timer.value)
                    timer.value = 0
                    qrCodeText.value = ''
                    ElMessage.success('登录成功')
                    initCredential()
                    isShow.value = false
                }
                if (resp.msg == 'qr_state') {
                    switch (resp.data.data) {
                        case 'confirm':
                            qrCodeText.value = '未确认登录'
                            break
                        case 'timeout':
                            qrCodeText.value = '二维码已过期'
                            break
                        default:
                            qrCodeText.value = ''
                            break
                    }
                }
            } else {
                ElMessage.warning(resp.msg || '二维码状态请求错误')
            }
        })
        .catch((error) => ElMessage.error(error))
}

const closeDialog = () => {
    clearInterval(timer.value)
    timer.value = 0
}

onMounted(() => {
    initConfig()
    initCredential()
})
</script>
<template>
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
            <!-- <el-form-item label="粉丝牌等级" prop="modal_level">
                <el-input v-model="baseFormValue.modal_level" placeholder="粉丝牌等级" type="text" min="0" />
            </el-form-item>
            <el-form-item label="用户等级" prop="user_level">
                <el-radio-group v-model="baseFormValue.user_level">
                    <template v-for="item in dropdownMenu">
                        <el-radio :value="item.value">{{ item.key }}</el-radio>
                    </template>
                </el-radio-group>
            </el-form-item> -->
            <el-form-item label="点歌指令" prop="sing_prefix">
                <el-input v-model="baseFormValue.sing_prefix" placeholder="点歌指令" type="text" />
            </el-form-item>
            <!-- <el-form-item label="点歌cd" prop="sing_cd">
                <el-input v-model="baseFormValue.sing_cd" placeholder="点歌cd，单位：秒" type="text" min="0" />
            </el-form-item> -->
            <el-form-item>
                <el-button type="primary" @click="addOrUpdateConfig()">保存</el-button>
            </el-form-item>
        </el-form>
    </el-card>
    <el-divider />
    <el-card>
        <template #header>
            <div class="card-header">
                <span>账号设置</span>
                <el-alert title="未登录账号无法获取到弹幕用户昵称等信息，如有需要可添加一个小号" type="warning" :closable="false" />
            </div>
        </template>
        <div class="mb-4 flex items-center">
            <el-button type="primary" @click="addSub">新增</el-button>
        </div>
        <div style="height: 300px;">
            <el-auto-resizer>
                <template #default="{ width, height }">
                    <el-table-v2 :columns="credentialColumns" :data="credentialList" :width="width" :height="height"
                        fixed></el-table-v2>
                </template>
            </el-auto-resizer>
        </div>
    </el-card>
    <el-dialog v-model="isShow" title="新增" width="720" @close="closeDialog" destroy-on-close>
        <div class="avatar-image-container">
            <img :src="qrCode" alt="qrcode" class="avatar" referrerpolicy="no-referrer" />
            <div class="code-bage" v-if="qrCodeText.length > 0">{{ qrCodeText }}</div>
        </div>
    </el-dialog>
</template>
<style scoped>
.avatar-image-container {
    position: relative;
    display: block;
}

.avatar {
    margin: 0 auto;
    display: block;
    width: 240px;
    height: 240px;
}

.code-bage {
    width: 240px;
    height: 240px;
    font-size: 36px;
    opacity: 0.6;
    text-align: center;
    color: #000;
    background-color: #fff;
    z-index: 1;
    user-select: none;
    line-height: 240px;
    text-decoration: none;
    font-weight: bold;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translateX(-50%) translateY(-50%);
}
</style>
