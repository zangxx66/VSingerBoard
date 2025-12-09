<script setup lang="ts">
import { ElMessage, ElMessageBox } from "element-plus"
import { CloseBold, Download, Delete, EditPen, CopyDocument, DocumentChecked } from "@element-plus/icons-vue"
import { exportExcel, timespanToString, getNowTimespan, processDanmaku, copyToClipboard } from "@/utils"
import type { Column } from "exceljs"

const singDialogRef = ref<null | InstanceType<typeof AddSingDialog>>()
const config = reactive<LiveModel>({
    douyin_romm_id: 0,
    bilibili_room_id: 0,
    douyin_ws_status: -1,
    bilibili_ws_status: -1
})
const danmakuStore = useDanmakuStore()
const infiniteList = ref<HTMLDivElement | null>(null)
let wsSend: (data: string | ArrayBuffer | Blob, useBuffer?: boolean | undefined) => boolean

const load = () => console.log("load")

const copy = (msg_id: number, txt: string) => {
    copyToClipboard(txt)
    danmakuStore.updateDanmakuStatus(msg_id, 1)
    ElMessage.success("拷贝成功")
}

const remove = (danmaku: DanmakuModel) => {
    danmakuStore.removeDanmakuList(danmaku)
    wsSend(`{"type":"delete","data":${danmaku.msg_id}}`)
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
            danmakuStore.clearDanmakuList()
            wsSend(`{"type":"clear","data":""}`)
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
        { header: "平台", key: "source", width: 50 }
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

const getDanmaku = () => {
    const { status, open, send } = useWebSocket("ws://127.0.0.1:8080", {
        autoReconnect: true,
        autoClose: true,
        heartbeat: {
            message: `{"type":"echo","data":"heartbeat"}`,
            interval: 5000,
            pongTimeout: 10000
        },
        onMessage: (ws: WebSocket, event: MessageEvent) => {
            const data = JSON.parse(event.data) as WsModel
            if (data.type == "echo") {
                return
            }
            else if (data.type == "del") {
                const delList = data.data as Array<DelListModel>
                const result = danmakuList.value.filter(item => !delList.some(delItem => delItem.msg_id === item.msg_id))
                danmakuStore.setDanmakuList(result)
            }
            else if (data.type == "add") {
                const value = data.data as Array<DanmakuModel>
                const douyin = value.filter(item => item.source == "douyin")
                const bilibili = value.filter(item => item.source == "bilibili")
                const result = [...danmakuList.value, ...processDanmaku(douyin, "douyin"), ...processDanmaku(bilibili, "bilibili")]
                danmakuStore.setDanmakuList(result)
            }
            else if (data.type == "live_config") {
                Object.assign(config, data.data)
            }
            else if (data.type == "bili_room_change") {
                config.bilibili_room_id = data.data
            }
            else if (data.type == "bili_status_change") {
                config.bilibili_ws_status = data.data
            }
            else if (data.type == "douyin_room_change") {
                config.douyin_romm_id = data.data
            }
            else if (data.type == "douyin_status_change") {
                config.douyin_ws_status = data.data
            }
        }
    })
    wsSend = send
    send(`{"type":"live_config","data":""}`)
}

const openDanmakuWindow = async () => {
    const isBundle = await window.pywebview.api.is_bundle()
    const port = isBundle ? 8000 : 5173
    const a = document.createElement("a")
    a.href = `http://127.0.0.1:${port}/danmaku`
    a.target = "_blank"
    a.click()
    a.remove()
}

const openSingDialog = () => {
    singDialogRef.value && singDialogRef.value.openDialog()
}

const danmakuList = computed(() => {
    const list = danmakuStore.getDanmakuList()
    return list
})

watch(danmakuList, async () => {
    await nextTick()
    infiniteList.value && infiniteList.value.scrollTo({ behavior: "smooth", top: infiniteList.value.scrollHeight })
})

onMounted(() => {
    const height = window.innerHeight * 0.9
    const dom = document.querySelector(".chat-main") as HTMLElement
    dom.style.overflow = "hidden"

    const infiniteListDom = document.querySelector(".chat-infinite-list") as HTMLElement
    const listHeight = height * 0.8
    infiniteListDom.style.height = `${listHeight}px`

    getDanmaku()

    if (import.meta.env.DEV) {
        danmakuStore.setDanmakuList([{
            msg_id: 0,
            uid: 0,
            uname: "uname",
            msg: "last love",
            send_time: getNowTimespan(),
            source: "bilibili",
            medal_name: "雾了",
            medal_level: 12,
            guard_level: 0,
            status: 0
        },
        {
            msg_id: 1,
            uid: 1,
            uname: "uname",
            msg: "last dance",
            send_time: getNowTimespan(),
            source: "douyin",
            medal_name: "雾了",
            medal_level: 10,
            guard_level: 2,
            status: 0
        },
        {
            msg_id: 2,
            uid: 2,
            uname: "uname",
            msg: "last dance",
            send_time: getNowTimespan(),
            source: "douyin",
            medal_name: "雾了",
            medal_level: 10,
            guard_level: 1,
            status: 0
        },
        {
            msg_id: 3,
            uid: 3,
            uname: "uname",
            msg: "last dance",
            send_time: getNowTimespan(),
            source: "douyin",
            medal_name: "",
            medal_level: 10,
            guard_level: 1,
            status: 0
        }])
    }
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
                <div class="chat-infinite-list" ref="infiniteList" v-infinite-scroll="load">
                    <template v-for="item in danmakuList">
                        <div class="chat-infinite-list-item">
                            <img :src="`/assets/images/${item.source}.png`" class="source-img" :alt="item.source"
                                width="24" />
                            <el-text tag="span" class="chat-tag">
                                <template v-if="item.medal_level > 0">
                                    <template v-if="item.source == 'bilibili'">
                                        <fans-medal :medal_name="item.medal_name" :medal_level="item.medal_level"
                                            :guard_level="item.guard_level" />
                                    </template>
                                    <template v-if="item.source == 'douyin'">
                                        <fans-club :medal_name="item.medal_name" :medal_level="item.medal_level"
                                            :guard_level="item.guard_level" />
                                    </template>
                                </template>
                                <template v-if="item.html != undefined && item.html.length > 0">
                                    {{ item.uname }}；
                                    <el-text v-html="item.html"></el-text>
                                </template>
                                <template v-else>
                                    {{ item.uname }}： {{ item.msg }}
                                </template>
                            </el-text>

                            <el-tooltip v-if="item.status == 0" placement="bottom">
                                <template #content>
                                    <span>复制点歌</span>
                                </template>
                                <span class="chat-close" @click="copy(item.msg_id, item.msg)">
                                    <el-icon>
                                        <CopyDocument />
                                    </el-icon>
                                </span>
                            </el-tooltip>
                            <el-tooltip v-if="item.status == 1" placement="bottom">
                                <template #content>
                                    <span>已复制</span>
                                </template>
                                <span class="chat-close">
                                    <el-icon>
                                        <DocumentChecked />
                                    </el-icon>
                                </span>
                            </el-tooltip>
                            <el-tooltip placement="bottom">
                                <template #content>
                                    <span>移除点歌</span>
                                </template>
                                <span class="chat-close" @click="remove(item)">
                                    <el-icon>
                                        <CloseBold />
                                    </el-icon>
                                </span>
                            </el-tooltip>
                        </div>
                    </template>
                </div>
                <template #footer>
                    <div class="chat-card-footer">
                        <el-button type="primary" @click="openSingDialog">
                            手动点歌
                            <el-icon>
                                <EditPen />
                            </el-icon>
                        </el-button>
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
            <addSingDialog ref="singDialogRef"></addSingDialog>
        </el-main>
    </el-container>
</template>
