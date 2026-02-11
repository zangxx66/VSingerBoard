<script setup lang="tsx">
import { ElMessage, ElMessageBox, ElText, ElButton, ElSwitch, type Column } from 'element-plus'
import { Delete, Refresh } from '@element-plus/icons-vue'
import { request } from '@/api'

const isShow = ref(false)
const btnLoading = ref(false)
const timer = ref(0)
const qrCode = ref('')
const qrCodeText = ref('')
const credentialList = ref(Array<BiliCredentialModel>())

const credentialColumns: Column<any>[] = [
    {
        key: 'uid',
        dataKey: 'uid',
        title: 'uid',
        width: 200,
        cellRenderer: ({ cellData: uid }) => <ElText>{uid} </ElText>,
    },
    {
        key: 'uname',
        dataKey: 'uname',
        title: '昵称',
        width: 300,
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
                style="--el-switch-off-color: #ff4949; --el-switch-on-color: #13ce66"
                activeText="启用"
                inactiveText="禁用"
                onChange={(val: string | number | boolean) => {
                    statusMutation.mutate({ id: rowData.id, enable: val })
                }}
            >
                {' '}
            </ElSwitch>
        ),
    },
    {
        key: 'operations',
        title: '操作',
        width: 200,
        maxWidth: 1020,
        minWidth: 100,
        cellRenderer: ({ rowData }) => (
            <>
                <ElButton
                    type="success"
                    icon={Refresh}
                    loading={btnLoading.value}
                    onClick={(_evt: MouseEvent) => refreshSub(rowData.id)}
                >
                    刷新凭证
                </ElButton>
                <ElButton
                    type="danger"
                    icon={Delete}
                    onClick={(_evt: MouseEvent) => removeSub(rowData.id)}
                >
                    删除
                </ElButton>
            </>
        ),
    },
]

const { data: list, refetch, isFetching } = useGetBilibiliCredential()

const statusMutation = useMutation({
    mutationFn: async (params: object) => await request.updateBiliCredential({ data: params }),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "设置失败")
        } else {
            refetch()
        }
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

const checkQrCodeMutation = useMutation({
    mutationFn: async () => await request.checkQrCode({}),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "请求失败")
        } else {
            if (response.msg == 'success') {
                clearInterval(timer.value)
                timer.value = 0
                qrCodeText.value = ''
                ElMessage.success('登录成功')
                refetch()
                isShow.value = false
            }
            if (response.msg == 'qr_state') {
                switch (response.data.data) {
                    case 'confirm':
                        qrCodeText.value = '已扫码'
                        break
                    case 'timeout':
                        qrCodeText.value = '二维码已过期'
                        break
                    case 'done':
                        clearInterval(timer.value)
                        timer.value = 0
                        qrCodeText.value = ''
                        ElMessage.success('登录成功')
                        refetch()
                        isShow.value = false
                        break
                    default:
                        qrCodeText.value = ''
                        break
                }
            }
        }
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

const qrCodeMutation = useMutation({
    mutationFn: async () => await request.getBiliCredentialCode({}),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "获取失败")
        } else {
            qrCode.value = response.data.data
            timer.value = setInterval(checkQrCodeMutation.mutate, 3000)
            isShow.value = true
        }
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

const deleteMutation = useMutation({
    mutationFn: async (params: number) => await request.deleteBiliCredential({ id: params }),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "请求失败")
        } else {
            refetch()
        }
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

const refreshMutation = useMutation({
    mutationFn: async (params: number) => await request.refreshBiliCredential({ id: params }),
    onSuccess: (response) => {
        if (response.code != 0) {
            ElMessage.warning(response.msg || "请求失败")
        } else {
            ElMessage.success("刷新完成")
        }
        btnLoading.value = false
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

/** 删除凭证 */
const removeSub = (id: number) => {
    ElMessageBox.confirm('是否删除？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
        .then(() => deleteMutation.mutate(id))
        .catch((error) => {
            if ('string' == typeof error && 'cancel' == error) return
            ElMessage.error(error)
        })
}

/** 刷新凭证 */
const refreshSub = (id: number) => {
    btnLoading.value = true
    refreshMutation.mutate(id)
}

const closeDialog = () => {
    clearInterval(timer.value)
    timer.value = 0
}

watch(isFetching, () => {
    if (list.value) {
        credentialList.value = list.value
    }
})
</script>
<template>
    <el-card>
        <template #header>
            <div class="b-credential-card-header">
                <span>账号设置</span>
                <el-alert
title="未登录账号无法获取到弹幕用户昵称等信息，如有需要可添加一个小号" type="warning" :closable="false"
                    style="margin-top: 1rem;" />
            </div>
        </template>
        <div class="mb-4 flex items-center">
            <el-button type="primary" @click="qrCodeMutation.mutate()">新增</el-button>
        </div>
        <div v-loading="isFetching" style="height: 300px;padding-top: 1rem;">
            <el-auto-resizer>
                <template #default="{ width, height }">
                    <el-table-v2
:columns="credentialColumns" :data="credentialList" :width="width" :height="height"
                        fixed></el-table-v2>
                </template>
            </el-auto-resizer>
        </div>
    </el-card>
    <el-dialog v-model="isShow" title="新增" width="720" destroy-on-close @close="closeDialog">
        <div class="qcode-image-container">
            <img :src="qrCode" alt="qrcode" class="qcode" referrerpolicy="no-referrer" />
            <div v-if="qrCodeText.length > 0" class="qcode-bage">{{ qrCodeText }}</div>
        </div>
    </el-dialog>
</template>
