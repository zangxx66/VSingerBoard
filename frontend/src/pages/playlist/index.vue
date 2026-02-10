<script setup lang="tsx">
import { request } from "@/api"
import {
    ElMessage,
    ElMessageBox,
    ElButton,
    type Column as elColumn,
    type UploadFile,
    type UploadFiles,
} from "element-plus"
import { Search, Download, Upload, Delete, EditPen } from "@element-plus/icons-vue"
import type { Column as execlCoumn } from "exceljs"

defineOptions({
    name: "playlist"
})

const queryClient = useQueryClient()

const exportLoading = ref(false)
const importLoading = ref(false)
const total = ref(0)
const cardRef = useTemplateRef("playlistDataCard")
const playlistInfiniteList = useTemplateRef("playlistInfiniteList")
const addPlaylistDialogRef = useTemplateRef("addPlaylistDialogRef")
const baseFormValue = reactive<RequestPlaylist>({
    keyword: "",
    size: 20
})

const { data: response, refetch, fetchNextPage, isFetching } = usePlaylistInInfinite(baseFormValue)
const list = computed(() => response.value?.pages.flatMap(item => {
    total.value = item.total
    return item.rows
}).filter(Boolean))

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

// 删除
const deleteMutation = useMutation({
    mutationFn: async (params: number[]) => await request.deletePlaylist({ data: params }),
    onSuccess: (data, variables) => {
        if (data.code != 0) {
            ElMessage.warning(data.msg)
        } else {
            const indicesSet = new Set(variables)
            const newList = response.value?.pages.flatMap(item => item.rows).filter(item => !indicesSet.has(item.id)) ?? []
            queryClient.setQueryData(
                [request.getPlaylistList.name],
                () => ({
                    pages: [{ total: total.value - variables.length, rows: newList }]
                })
            )
        }
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

// 导入
const importMutation = useMutation({
    mutationFn: async (params: PlaylistModel[]) => await request.importPlaylist({ data: params }),
    onSuccess: (data) => {
        if (data.code != 0) {
            ElMessage.warning(data.msg)
        } else {
            refetch()
        }
        importLoading.value = false
    },
    onError: (error) => {
        ElMessage.error(error.message)
    }
})

/** 新增/编辑弹窗 */
const addOrEditPlaylist = (rowData?: any) => {
    if (rowData) rowData = rowData as PlaylistModel
    addPlaylistDialogRef.value && addPlaylistDialogRef.value.openDialog(rowData)
}

const allDeletePlaylist = () => {
    const checkedIds = list.value?.filter(item => item.checked).map(item => item.id)
    if (checkedIds) deletePlaylist(checkedIds)
}

/** 删除 */
const deletePlaylist = (ids: number[]) => {
    ElMessageBox.confirm("是否删除？", "提示", {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
    })
        .then(() => {
            deleteMutation.mutate(ids)
        })
        .catch(error => {
            if ('string' == typeof error && 'cancel' == error) return
            ElMessage.error(error)
        })
}

/** 新增/编辑歌曲的回调 */
const emitSubmit = (result: PlaylistModel) => {
    refetch()
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
    importMutation.mutate(result)
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

const search = () => {
    refetch()
}

const nextPage = (remainDistance: number) => {
    if (list.value && list.value.length < total.value) {
        fetchNextPage()
    }
}

onMounted(() => {
    const height = window.innerHeight * 0.9
    cardRef.value?.$el.style.setProperty("overflow", "hidden")

    const listHeight = height * 0.6
    playlistInfiniteList.value?.style.setProperty("height", `${listHeight}px`)
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
                <el-button type="danger" @click="allDeletePlaylist()" :disabled="list?.length == 0">全部删除</el-button>
            </div>
            <el-card class="playlist-data-card" v-loading="isFetching" ref="playlistDataCard">
                <template #default>
                    <div class="chat-infinite-list" ref="playlistInfiniteList">
                        <el-auto-resizer>
                            <template #default="{ width, height }">
                                <el-table-v2 :columns="dataColumns" :data="list || []" :width="width" :height="height"
                                    @end-reached="nextPage" fixed></el-table-v2>
                            </template>
                        </el-auto-resizer>
                    </div>
                </template>
                <template #footer>
                    <div style="display: flex;">
                        <div style="width: 100%;flex-direction: row-reverse;display: flex;gap: 10px;">
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
            <add-playlist-dialog @submit="emitSubmit" ref="addPlaylistDialogRef" />
        </el-main>
    </el-container>
</template>