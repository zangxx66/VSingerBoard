<script setup lang="ts">
import { ref, reactive, onMounted, defineAsyncComponent, nextTick, watch } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { CloseBold, Download, Delete } from "@element-plus/icons-vue"
import { exportExcel, timespanToString, getNowTimespan, processDanmaku } from "@/utils"
import { useClipboard, useWebSocket } from "@vueuse/core"
import type { Column } from "exceljs"
import { useIntervalStore } from "@/stores"

const PlatformStatus = defineAsyncComponent(() => import("@/components/home/platformStatus.vue"))
const danmakuList = ref(Array<DanmakuModel>())
const config = reactive<LiveModel>({
    douyin_romm_id: 0,
    bilibili_room_id: 0,
    douyin_ws_status: -1,
    bilibili_ws_status: -1
})
const intervalStore = useIntervalStore()
const infiniteList = ref<HTMLDivElement | null>(null)

const initConfig = async() => {
    const data = await window.pywebview.api.get_live_config()
    Object.assign(config, data)
}

const load = () => console.log("load")

const copyToClipboard = (txt: string) => {
    const { copy } = useClipboard({
        source: txt
    })
    copy(txt)
    ElMessage.success("拷贝成功")
}

const remove = (danmaku: DanmakuModel) => {
    const index = danmakuList.value.indexOf(danmaku)
    if(index > -1){
        danmakuList.value.splice(index, 1)
    }
}

const clear = () => {
    ElMessageBox.confirm(
        "是否清空点歌列表",
        "提示",
        {
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            type: "warning",
        }
    )
    .then(() => {
        danmakuList.value = []
    })
    .catch((error) => {
        if ('string' == typeof error && 'cancel' == error) return
        ElMessage.error(error)
    })
}

const exportFile = () => {
    const columns: Partial<Column>[] = [
        { header: "日期", key: "date", width: 50 },
        { header: "昵称", key: "uname", width: 50 },
        { header: "歌名", key: "song", width: 50 },
        { header: "平台", key: "source", width: 50}
    ]

    const data = danmakuList.value.map(item => ({
        date: timespanToString(item.send_time),
        uname: item.uname,
        song: item.msg,
        source: item.source == "bilibili" ? "B站" : "抖音",
    }))

    const filename = `点歌列表_${getNowTimespan()}`

    exportExcel(columns, data, filename)
}


const appendDanmaku = async(list: DanmakuModel[], platform: "bilibili" | "douyin") => {
    const result = processDanmaku(list, platform)
    danmakuList.value.push(...result)
    if(infiniteList.value && list.length > 0){
        await nextTick()
        infiniteList.value.scrollTo({ behavior: "smooth", top: infiniteList.value.scrollHeight })
    }
}

const getDanmaku = () => {
    const { status, open } = useWebSocket("ws://127.0.0.1:8080", {
        autoReconnect: true,
        autoClose: true,
        heartbeat: {
            message: "heartbeat",
            interval: 5000,
            pongTimeout: 10000
        },
        onMessage: (ws: WebSocket, event: MessageEvent) => {
            if(event.data.startsWith("Echo")){
                return
            }else{
                const value = JSON.parse(event.data) as Array<DanmakuModel>
                const douyin = value.filter(item => item.source == "douyin")
                const bilibili = value.filter(item => item.source == "bilibili")
                console.log(value)
                danmakuList.value = [...danmakuList.value, ...processDanmaku(douyin, "douyin"), ...processDanmaku(bilibili, "bilibili")]
            }
        }
    })
}

const openDanmakuWindow = async() => {
    const isBundle = await window.pywebview.api.is_bundle()
    const port = isBundle ? 8000 : 5173
    const a = document.createElement("a")
    a.href = `http://127.0.0.1:${port}/danmaku`
    a.target = "_blank"
    a.click()
    a.remove()
}

watch(danmakuList, async () => {
    await nextTick()
    infiniteList.value && infiniteList.value.scrollTo({ behavior: "smooth", top: infiniteList.value.scrollHeight })
})

onMounted(() => {
    const height = window.innerHeight - 100
    const dom = document.querySelector(".chat-main") as HTMLElement
    dom.style.height = `${height}px`
    dom.style.overflow = "hidden"

    const infiniteListDom = document.querySelector(".infinite-list") as HTMLElement
    const listHeight = height * 0.7
    infiniteListDom.style.height = `${listHeight}px`

    getDanmaku()

    intervalStore.addInterval("get_live_config", initConfig, 1000)
})
</script>
<template>
    <el-container class="chat-container">
        <el-main class="chat-main">
            <el-card class="chat-card">
                <template #header>
                    <div class="card-header">
                        <span>
                            点歌列表
                            <link-icon style="cursor: pointer;" @click="openDanmakuWindow" />
                        </span>
                    </div>
                </template>
                <div class="infinite-list" ref="infiniteList" v-infinite-scroll="load">
                    <template v-for="item in danmakuList">
                        <div class="infinite-list-item">
                            <template v-if="item.source == 'bilibili'">
                                <img src="/assets/images/bilibili.png" class="source-img" alt="bilibili" width="24" />
                            </template>
                            <template v-else-if="item.source == 'douyin'">
                                <img src="/assets/images/douyin.png" class="source-img" alt="douyin" width="24" />
                            </template>
                            <el-tooltip placement="bottom">
                                <template #content>
                                    <span>点击复制歌名：{{ item.msg }}</span>
                                </template>
                                <el-text tag="span" class="chat-tag" @click="copyToClipboard(item.msg)">
                                    <template v-if="item.html != undefined">
                                        {{ item.uname }}；
                                        <el-text v-html="item.html" style="display: flex;"></el-text>
                                    </template>
                                    <template v-else>
                                        {{ item.uname }}： {{ item.msg }}
                                    </template>
                                </el-text>
                            </el-tooltip>

                            <el-tooltip placement="bottom">
                                <template #content>
                                    <span>移除点歌：{{ item.msg }}</span>
                                </template>
                                <el-text tag="span" class="chat-close" @click="remove(item)">
                                    <el-icon>
                                        <CloseBold />
                                    </el-icon>
                                </el-text>
                            </el-tooltip>
                        </div>
                    </template>
                </div>
                <template #footer>
                    <div class="card-footer">
                        <el-button type="danger" :disabled="danmakuList.length == 0" @click="clear">
                            清空点歌列表
                            <el-icon class="el-icon--right">
                                <Delete />
                            </el-icon>
                        </el-button>
                        <el-button type="success" :disabled="danmakuList.length == 0" @click="exportFile">
                            导出点歌列表
                            <el-icon class="el-icon--right">
                                <Download />
                            </el-icon>
                        </el-button>
                        <div class="card-footer-right">
                            <PlatformStatus platform="douyin" v-if="config.douyin_romm_id > 0"
                                :roomId="config.douyin_romm_id" :wsStatus="config.douyin_ws_status" />
                            <PlatformStatus platform="bilibili" v-if="config.bilibili_room_id > 0"
                                :roomId="config.bilibili_room_id" :wsStatus="config.bilibili_ws_status" />
                        </div>
                    </div>
                </template>
            </el-card>
        </el-main>
    </el-container>
</template>
<style scoped>
.chat-card {
    height: 100%;
}

.infinite-list {
    padding: 0;
    margin: 0;
    list-style: none;
    overflow: auto;
}

.infinite-list-item {
    width: 95%;
    display: flex;
    margin: 10px;
    height: 50px;
    text-align: left;
    align-items: center;
    justify-content: center;
    background-color: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
}

.chat-tag {
    display: inline-block;
    width: 90%;
    cursor: pointer;
    margin-left: 1%;
}

.chat-close {
    width: 1%;
    margin-right: 1%;
    cursor: pointer;
}

.source-img {
    margin: 1px;
    height: 24px;
}

.card-header {
    height: 24px;
    display: flex;
}

.card-footer-right {
    float: right;
    display: flex;
}
</style>