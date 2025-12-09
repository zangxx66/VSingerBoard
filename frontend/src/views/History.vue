<script setup lang="ts">
import { request } from "@/api"
import { ElMessage } from "element-plus"
import { Search } from "@element-plus/icons-vue"
import { timespanToString, getEndOfDayTimespan } from "@/utils"

const loading = ref(false)
const total = ref(0)
const page = ref(1)
const size = ref(20)
const dateRange = ref<[number, number]>()
const baseFormValue = reactive({
    uname: "",
    song_name: "",
    source: "all",
    start_time: 0,
    end_time: 0,
    page: page.value,
    size: size.value
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
    if(!val) {
        baseFormValue.start_time = 0
        baseFormValue.end_time = 0
        return
    }
    baseFormValue.start_time = val[0]
    baseFormValue.end_time = getEndOfDayTimespan(val[1])
}

const list = ref<Array<SongHistoryModel>>()

const load = () => {
    loading.value = true
    request.getHistoryList(baseFormValue).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
            loading.value = false
            return
        }
        total.value = resp.data.total
        list.value = resp.data.rows
        loading.value = false
    }).catch(error => {
        ElMessage.error(error)
        loading.value = false
    })
}

const search = () => {
    page.value = 1
    load()
}

onMounted(() => {
    const height = window.innerHeight * 0.9
    const dom = document.querySelector(".history-data-card") as HTMLElement
    dom.style.overflow = "hidden"

    const listHeight = height * 0.6
    const infiniteListDom = document.querySelector(".chat-infinite-list") as HTMLElement
    infiniteListDom.style.height = `${listHeight}px`

    load()
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
            <el-card class="history-data-card" v-loading="loading">
                <template #default>
                    <div class="chat-infinite-list">
                        <template v-for="item in list">
                            <div class="chat-infinite-list-item">
                                <img :src="`/assets/images/${item.source}.png`" class="source-img" :alt="item.source"
                                    width="24" />
                                <text tag="span" class="chat-tag">
                                    {{ item.uname }}：{{ item.song_name }}
                                </text>
                                <span style="width: 15%;">
                                    {{ timespanToString(item.create_time) }}
                                </span>
                            </div>
                        </template>
                        <template v-if="list?.length == 0">
                            <el-empty description="没有数据" />
                        </template>
                    </div>
                </template>
                <template #footer>
                    <el-pagination background layout="prev, pager, next" :total="total" v-model:page-size="size"
                        v-model:current-page="page" @change="load" />
                </template>
            </el-card>
        </el-main>
    </el-container>
</template>