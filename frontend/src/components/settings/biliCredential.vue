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
        width: 200,
        maxWidth: 1020,
        minWidth: 100,
        cellRenderer: ({ rowData }) => (
            <>
                <ElButton
                    type="success"
                    icon={Refresh}
                    loading={btnLoading.value}
                    onClick={(evt: MouseEvent) => refreshSub(rowData.id)}
                >
                    刷新凭证
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

const initCredential = () => {
    request.getBiliCredntialList({}).then((response) => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            credentialList.value = resp.data.rows
        }
    }).catch(error => {
        ElMessage.error(error)
    })
}

/** 更改状态 */
const changeStatus = (val: string | number | boolean, id: number) => {
    request.UpdateBiliCredential({ data: { id: id, enable: val } })
        .then(response => {
            const resp = response.data as ResponseModel
            if (resp.code != 0) {
                ElMessage.warning(resp.msg || "设置失败")
                revertLocalValue(id, !val)
                return
            }
            ElMessage.success(resp.msg || "设置成功")
            credentialList.value.forEach((value, index, array) => {
                if (value.id == id) return
                value.enable = !val
            })
        })
        .catch(error => {
            ElMessage.error(error)
            revertLocalValue(id, !val)
        })
}

/** 修改状态失败时恢复原样 */
const revertLocalValue = (id: number, value: boolean | string | number) => {
    const index = credentialList.value.findIndex(item => item.id === id)
    if (index !== -1) {
        (credentialList.value[index] as any)["enable"] = value
    }
}

/** 打开登录二维码弹窗 */
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

/** 删除凭证 */
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

/** 刷新凭证 */
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

/** 轮询二维码状态 */
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
                            qrCodeText.value = '已扫码'
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
    initCredential()
})
</script>
<template>
    <el-card>
        <template #header>
            <div class="b-credential-card-header">
                <span>账号设置</span>
                <el-alert title="未登录账号无法获取到弹幕用户昵称等信息，如有需要可添加一个小号" type="warning" :closable="false" style="margin-top: 1rem;" />
            </div>
        </template>
        <div class="mb-4 flex items-center">
            <el-button type="primary" @click="addSub">新增</el-button>
        </div>
        <div style="height: 300px;padding-top: 1rem;">
            <el-auto-resizer>
                <template #default="{ width, height }">
                    <el-table-v2 :columns="credentialColumns" :data="credentialList" :width="width" :height="height"
                        fixed></el-table-v2>
                </template>
            </el-auto-resizer>
        </div>
    </el-card>
    <el-dialog v-model="isShow" title="新增" width="720" @close="closeDialog" destroy-on-close>
        <div class="qcode-image-container">
            <img :src="qrCode" alt="qrcode" class="qcode" referrerpolicy="no-referrer" />
            <div class="qcode-bage" v-if="qrCodeText.length > 0">{{ qrCodeText }}</div>
        </div>
    </el-dialog>
</template>
