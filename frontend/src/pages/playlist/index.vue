<script setup lang="tsx">
import { request } from "@/api"
import type { FunctionalComponent } from "vue"
import { ElMessage, ElMessageBox, ElButton, ElCheckbox, useLocale, type Column as elColumn, type CheckboxValueType, type UploadFile, type UploadFiles } from "element-plus"
import { Search, Download, Upload, Delete, EditPen } from "@element-plus/icons-vue"
import { getNowTimespan, exportExcel, importExcel } from "@/utils"
import type { Column as execlCoumn } from "exceljs"

type SelectionCellProps = {
    value: boolean
    intermediate?: boolean
    ariaLabel?: string
    onChange: (value: CheckboxValueType) => void
}

const { t } = useLocale()

const SelectionCell: FunctionalComponent<SelectionCellProps> = ({
    value,
    intermediate = false,
    ariaLabel,
    onChange,
}) => {
    return (
        <ElCheckbox onChange={onChange} modelValue={value} ariaLabel={ariaLabel} indeterminate={intermediate} />
    )
}

const loading = ref(false)
const exportLoading = ref(false)
const importLoading = ref(false)
const total = ref(0)
const list = ref(Array<PlaylistModel>())
const cardRef = useTemplateRef("playlistDataCard")
const infiniteListRef = useTemplateRef("playlistInfiniteList")
const addPlaylistDialog = useTemplateRef("addPlaylistDialogRef")
const baseFormValue = reactive({
    keyword: "",
    page: 1,
    size: 20
})
const exportColumns: Partial<execlCoumn>[] = [
    { header: "歌曲名", key: "song_name", width: 50 },
    { header: "歌手", key: "singer", width: 50 },
    { header: "语种", key: "language", width: 25 },
    { header: "标签", key: "tag", width: 50 },
    { header: "是否SC曲目", key: "is_sc", width: 25, },
    { header: "SC曲目价格", key: "sc_price", width: 25 },
]
const importColumns: Partial<ImportColumn>[] = [
    { header: "歌曲名", key: "song_name", type: "string" },
    { header: "歌手", key: "singer", type: "string" },
    { header: "语种", key: "language", type: "string" },
    { header: "标签", key: "tag", type: "string" },
    { header: "是否SC曲目", key: "is_sc", type: "boolean" },
    { header: "SC曲目价格", key: "sc_price", type: "number" },
]
const dataColumns: elColumn<any>[] = [
    {
        key: "selection",
        width: 50,
        cellRenderer: ({ rowData }) => {
            const onChange = (value: CheckboxValueType) => (rowData.checked = value)
            return (
                <>
                    <SelectionCell value={rowData.checked} ariaLabel={t('el.table.selectRowLabel')} onChange={onChange} />
                </>
            )
        },
        headerCellRenderer: () => {
            const _data = unref(list)
            const onChange = (value: CheckboxValueType) => (list.value = _data.map(row => {
                row.checked = Boolean(value)
                return row
            }))
            const allSelected = _data.every(row => row.checked)
            const containsChecked = _data.some(row => row.checked)

            return (
                <>
                    <SelectionCell value={allSelected} intermediate={containsChecked && !allSelected} ariaLabel={t('el.table.selectAllLabel')} onChange={onChange} />
                </>
            )
        }
    },
    {
        key: "song_name",
        dataKey: "song_name",
        title: "歌名",
        width: 200,
    },
    {
        key: "singer",
        dataKey: "singer",
        title: "歌手",
        width: 200,
    },
    {
        key: "language",
        dataKey: "language",
        title: "语种",
        width: 200,
    },
    {
        key: "tag",
        dataKey: "tag",
        title: "标签",
        width: 200,
    },
    {
        key: "sc_price",
        dataKey: "sc_price",
        title: "SC曲目价格",
        width: 200,
    },
    {
        key: "operations",
        title: "操作",
        width: 200,
        cellRenderer: ({ rowData }) => (
            <>
                <ElButton type="success" icon={EditPen} onClick={(evt: MouseEvent) => addOrEditPlaylist(rowData)}>
                    编辑
                </ElButton>
                <ElButton type="default" icon={Delete} onClick={(evt: MouseEvent) => deletePlaylist([rowData.id])}>
                    删除
                </ElButton>
            </>
        )
    }
]

/** 新增/编辑弹窗 */
const addOrEditPlaylist = (rowData?: any) => {
    if (rowData) rowData = rowData as PlaylistModel
    addPlaylistDialog.value && addPlaylistDialog.value.openDialog(rowData)
}

const allDeletePlaylist = () => {
    const checkedIds = list.value.filter(item => item.checked).map(item => item.id)
    deletePlaylist(checkedIds)
}

/** 删除 */
const deletePlaylist = (ids: number[]) => {
    ElMessageBox.confirm("是否删除？", "提示", {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
        .then(() => request.deletePlaylist({ data: ids }))
        .then(response => {
            if (response.code != 0) {
                ElMessage.warning(response.msg)
                return
            }
            ElMessage.success(response.msg)
            const indicesSet = new Set(ids)
            list.value = list.value.filter(item => !indicesSet.has(item.id))
        })
        .catch(error => {
            if ('string' == typeof error && 'cancel' == error) return
            ElMessage.error(error)
        })
}

/** 新增/编辑歌曲的回调 */
const emitSubmit = (result: PlaylistModel) => {
    const model = list.value.find(item => item.id == result.id)
    if (model) {
        Object.assign(model, result)
        return
    }
    list.value.unshift(result)
}

/** 导入excel */
const importFile = async (uploadFile: UploadFile, uploadFiles: UploadFiles) => {
    importLoading.value = true
    if (!uploadFile) {
        importLoading.value = false
        return
    }

    const filenameArray = uploadFile.name.split('.')
    const fileType = filenameArray[filenameArray.length - 1]
    if (fileType != "xlsx") {
        ElMessage.warning("请上传xlsx格式的表格")
        importLoading.value = false
        return
    }

    const buffer = await uploadFile.raw?.arrayBuffer()
    const result = await importExcel<PlaylistModel>(importColumns, buffer)
    result.forEach(item => {
        item.id = 0
        item.create_time = getNowTimespan()
    })
    request.importPlaylist({ data: result }).then(response => {
        if (response.code != 0) {
            ElMessage.warning(response.msg)
        } else {
            ElMessage.success(response.msg)
        }
        importLoading.value = false
        search()
    }).catch(error => {
        ElMessage.error(error)
        importLoading.value = false
    })
}

/** 导出excel */
const exportFile = () => {
    const args: any = {}
    Object.assign(args, baseFormValue)
    args.page = 1
    args.size = total.value

    exportLoading.value = true
    request.getPlaylistList(args).then(response => {
        if (response.code != 0) {
            ElMessage.warning(response.msg)
            exportLoading.value = false
            return
        }
        const data = response.data.rows as Array<PlaylistModel>
        const exportData = data.map(item => ({
            song_name: item.song_name,
            singer: item.singer,
            is_sc: item.is_sc ? "是" : "否",
            sc_price: item.sc_price,
            language: item.language,
            tag: item.tag
        }))
        const filename = `歌单_${getNowTimespan()}`
        exportExcel(exportColumns, exportData, filename)
        exportLoading.value = false
    }).catch(error => {
        ElMessage.error(error)
        exportLoading.value = false
    })
}

/** 加载table数据 */
const load = () => {
    loading.value = true
    request.getPlaylistList(baseFormValue).then(response => {
        if (response.code != 0) {
            ElMessage.warning(response.msg)
            loading.value = false
            return
        }
        total.value = response.data.total
        const result = response.data.rows as Array<PlaylistModel>
        result.forEach(item => item.checked = false)
        list.value = result
        loading.value = false
    }).catch(error => {
        ElMessage.error(error)
        loading.value = false
    })
}

const search = () => {
    baseFormValue.page = 1
    load()
}

const isChecked = computed(() => {
    return list.value.filter(item => item.checked).length > 0 ? true : false
})

onMounted(() => {
    const height = window.innerHeight * 0.9
    cardRef.value?.$el.style.setProperty("overflow", "hidden")

    const listHeight = height * 0.6
    infiniteListRef.value?.style.setProperty("height", `${listHeight}px`)

    load()
})
</script>
<template>
    <el-container class="playlist-container">
        <el-main class="playlist-main">
            <el-card class="playlist-card">
                <template #header>
                    <div class="card-header">
                        <span>查询</span>
                    </div>
                </template>
                <el-form :model="baseFormValue" label-width="auto" inline class="inline-form">
                    <el-form-item label="关键词" prop="keyword">
                        <el-input v-model="baseFormValue.keyword" type="text" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="search">
                            <el-icon class="el-icon--left">
                                <Search />
                            </el-icon>
                            搜索
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-card>
            <el-divider />
            <div style="height: 40px;display: flex;">
                <el-button type="primary" @click="addOrEditPlaylist()">新增歌曲</el-button>
                <el-button type="danger" @click="allDeletePlaylist()" :disabled="!isChecked">全部删除</el-button>
            </div>
            <el-card class="playlist-data-card" v-loading="loading" ref="playlistDataCard">
                <template #default>
                    <div class="chat-infinite-list" ref="playlistInfiniteList">
                        <el-auto-resizer>
                            <template #default="{ width, height }">
                                <el-table-v2 :columns="dataColumns" :data="list" :width="width" :height="height"
                                    fixed></el-table-v2>
                            </template>
                        </el-auto-resizer>
                    </div>
                </template>
                <template #footer>
                    <div style="display: flex;">
                        <div style="width: 50%">
                            <el-pagination background layout="prev, pager, next" :total="total"
                                v-model:page-size="baseFormValue.size" v-model:current-page="baseFormValue.page"
                                @change="load" />
                        </div>
                        <div style="width: 50%;flex-direction: row-reverse;display: flex;gap: 10px;">
                            <el-upload action="#" :auto-upload="false" :show-file-list="false" :on-change="importFile"
                                accept=".xlsx">
                                <template #trigger>
                                    <el-button type="success" :loading="importLoading">
                                        导入歌单
                                        <el-icon class="el-icon--right">
                                            <Upload />
                                        </el-icon>
                                    </el-button>
                                </template>
                            </el-upload>
                            <el-button @click="exportFile" :loading="exportLoading">
                                导出歌单
                                <el-icon class="el-icon--right">
                                    <Download />
                                </el-icon>
                            </el-button>
                        </div>
                    </div>
                </template>
            </el-card>
            <AddPlaylistDialog @submit="emitSubmit" ref="addPlaylistDialogRef" />
        </el-main>
    </el-container>
</template>