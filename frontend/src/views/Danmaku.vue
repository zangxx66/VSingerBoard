<script setup lang="ts">
import { processDanmaku } from "@/utils"
import { useWebSocket } from "@vueuse/core"

const list = ref(Array<DanmakuModel>())
const infiniteList = ref<HTMLDivElement | null>(null)
const load = () => console.log("load")
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
            const data = JSON.parse(event.data) as WsModel
            if (data.type == "echo") {
                return
            }
            else if (data.type == "clear") {
                list.value = []
            }
            else if (data.type == "remove") {
                const value = data.data as DanmakuModel
                const danmaku = list.value.find(item => item.uid == value.uid && item.send_time == value.send_time)
                if (danmaku) {
                    const index = list.value.indexOf(danmaku)
                    if (index > -1) {
                        list.value.splice(index, 1)
                    }
                }
            }
            else if (data.type == "del") {
                const delList = data.data as Array<DelListModel>
                delList.forEach(item => {
                    let danmaku
                    if (item.song_name) {
                        danmaku = list.value.find(pItem => pItem.uid == item.uid && pItem.uname == item.uname && pItem.msg == item.song_name)
                    } else {
                        danmaku = list.value.find(pItem => pItem.uid == item.uid && pItem.uname == item.uname)
                    }
                    if (danmaku) {
                        const index = list.value.indexOf(danmaku)
                        if (index > -1) {
                            list.value.splice(index, 1)
                        }
                    }
                })
            }
            else {
                const value = data.data as Array<DanmakuModel>
                const douyin = value.filter(item => item.source == "douyin")
                const bilibili = value.filter(item => item.source == "bilibili")
                list.value = [...list.value, ...processDanmaku(douyin, "douyin"), ...processDanmaku(bilibili, "bilibili")]
            }
        }
    })
}

watch(list, async () => {
    await nextTick()
    infiniteList.value && infiniteList.value.scrollTo({ behavior: "smooth", top: infiniteList.value.scrollHeight })
})

onMounted(() => {
    document.title = "点歌列表"
    getDanmaku()
})
</script>
<template>
    <el-container class="danmaku-container">
        <el-main>
            <div class="danmaku-list" ref="infiniteList" v-infinite-scroll="load">
                <template v-for="item in list">
                    <div class="danmaku-list-item">
                        <div class="danmaku-sing">
                            <template v-if="item.html != undefined && item.html.length > 0">
                                <el-text v-html="item.html" style="display: flex;"></el-text>
                            </template>
                            <template v-else>
                                {{ item.msg }}
                            </template>
                        </div>
                        <div class="danmaku-uname">
                            {{ item.uname }}
                        </div>
                        <div class="danmaku-fans">
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
                        </div>
                    </div>
                </template>
            </div>
        </el-main>
    </el-container>
</template>