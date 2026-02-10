<script setup lang="ts">
import type { ScrollbarInstance, ScrollbarDirection } from "element-plus"
import { Search, Download } from "@element-plus/icons-vue"
import type { Column } from "exceljs"

defineOptions({
    name: "history"
})

const exportLoading = ref(false)
const total = ref(0)
const dateRange = ref<[number, number]>()
const cardRef = useTemplateRef("historyDataCard")
const chatInfiniteList = ref<ScrollbarInstance>()
const infiniteHeight = ref("0px")
const baseFormValue = reactive<RequestHistory>({
    uname: "",
    song_name: "",
    source: "all",
    start_time: 0,
    end_time: 0,
    size: 20
})
const platform = [
    {
        key: "全部",
        value: "all"
    },
    {
        key: "抖音",
        value: "douyin"
    },
    {
        key: "B站",
        value: "bilibili"
    }
]

const dateChange = (val: [number, number]) => {
    if (!val) {
        baseFormValue.start_time = 0
        baseFormValue.end_time = 0
        return
    }
    baseFormValue.start_time = val[0]
    baseFormValue.end_time = getEndOfDayTimespan(val[1])
}

const { data: response, refetch, fetchNextPage, isFetching } = useGetHistoryInfinite(baseFormValue)
const resultList = computed(() => response.value?.pages.flatMap(item => {
    total.value = item.total
    return item.rows
}).map(item => {
    const danmakus: DanmakuModel = {
        msg_id: item.id,
        uid: item.uid,
        uname: item.uname,
        msg: item.song_name,
        send_time: item.create_time,
        source: item.source,
        medal_name: "",
        medal_level: 0,
        guard_level: 0
    }
    const processDanmakus = processDanmaku([danmakus])
    const result: ResponseHistory = {
        ...item,
        song_name: processDanmakus[0].html || item.song_name,
        create_time_str: timespanToString(item.create_time)
    }
    return result
}).filter(Boolean))

const exportFile = () => {
    const columns: Partial<Column>[] = [
        { header: "日期", key: "date", width: 50 },
        { header: "昵称", key: "uname", width: 50 },
        { header: "歌名", key: "song", width: 50 },
        { header: "平台", key: "source", width: 50 }
    ]

    exportLoading.value = true
    const exportData = resultList.value?.map(item => ({
        date: timespanToString(item.create_time),
        uname: item.uname,
        song: item.song_name,
        source: item.source == "bilibili" ? "B站" : "抖音"
    }))
    const filename = `点歌历史记录_${getNowTimespan()}`
    const data = exportData as any[]
    exportExcel(columns, data, filename)

    exportLoading.value = false
}

const nextPage = (direction: ScrollbarDirection) => {
    if (direction === "bottom" && (resultList.value && resultList.value.length < total.value)) {
        fetchNextPage()
    }
}

onMounted(() => {
    const height = window.innerHeight * 0.9
    cardRef.value?.$el.style.setProperty("overflow", "hidden")

    const listHeight = height * 0.6
    infiniteHeight.value = `${listHeight}px`
})
</script>
<template>
    <el-container class="history-container">
        <el-main class="history-main">
            <el-card class="history-card">
                <template #header>
                    <div class="card-header">
                        <span>查询</span>
                    </div>
                </template>
                <el-form :model="baseFormValue" label-width="auto" inline class="inline-form">
                    <el-form-item label="歌名" prop="song_name">
                        <el-input v-model="baseFormValue.song_name" type="text" />
                    </el-form-item>
                    <el-form-item label="昵称" prop="uname">
                        <el-input v-model="baseFormValue.uname" type="text" />
                    </el-form-item>
                    <el-form-item label="点歌平台" prop="source">
                        <el-select v-model="baseFormValue.source" placeholder="请选择点歌平台">
                            <template v-for="item in platform">
                                <el-option :label="item.key" :value="item.value" />
                            </template>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="时间范围" prop="dateRange" style="width: 350px">
                        <el-date-picker v-model="dateRange" type="daterange" value-format="X" format="YYYY-MM-DD"
                            @change="dateChange" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="refetch()">
                            <el-icon class="el-icon--left">
                                <Search />
                            </el-icon>
                            搜索
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-card>
            <el-divider />
            <el-card class="history-data-card" v-loading="isFetching" ref="historyDataCard">
                <template #default>
                    <el-scrollbar class="chat-infinite-list" noresize :height="infiniteHeight" @end-reached="nextPage"
                        ref="chatInfiniteList">
                        <template v-for="item in resultList">
                            <div class="chat-infinite-list-item">
                                <img :src="`/images/${item.source}.png`" class="source-img" :alt="item.source"
                                    width="24" />
                                <text tag="span" class="chat-tag">
                                    {{ item.uname }}：<el-text style="display: flex;" v-html="item.song_name"></el-text>
                                </text>
                                <span style="width: 15%;">
                                    {{ item.create_time_str }}
                                </span>
                            </div>
                        </template>
                        <template v-if="resultList?.length == 0">
                            <el-empty description="没有数据" />
                        </template>
                    </el-scrollbar>
                </template>
                <template #footer>
                    <div style="display: flex;text-align: right;">
                        <el-button type="success" :disabled="resultList?.length == 0" @click="exportFile"
                            :loading="exportLoading">
                            导出历史记录
                            <el-icon class="el-icon--right">
                                <Download />
                            </el-icon>
                        </el-button>
                    </div>
                </template>
            </el-card>
        </el-main>
    </el-container>
</template>