<script setup lang="ts">
import { processDanmaku } from "@/utils"
import type { ScrollbarInstance } from "element-plus"

defineOptions({
    name: "danmaku"
})

const list = ref(Array<DanmakuModel>())
const infiniteList = ref<ScrollbarInstance>()
const getDanmaku = () => {
    const { status, open } = useWebSocket("ws://127.0.0.1:8080", {
        autoReconnect: true,
        autoClose: true,
        heartbeat: {
            message: `{"type":"echo","data":"heartbeat"}`,
            interval: 5000,
            pongTimeout: 10000
        },
        onMessage: (ws: WebSocket, event: MessageEvent) => {
            const data = JSON.parse(event.data) as WsModel
            const handler = messageHandlers[data.type]
            if (handler) {
                handler(data.data)
            }
        }
    })
}

const messageHandlers: Record<string, (data: any) => void> = {
    "echo": () => {
        return
    },
    "clear": () => {
        list.value = []
    },
    "remove": (data: number) => {
        list.value = list.value.filter(item => item.msg_id != data)
    },
    "del": (data: Array<DelListModel>) => {
        list.value = list.value.filter(item => !data.some(delItem => delItem.msg_id === item.msg_id))
    },
    "add": (data: Array<DanmakuModel>) => {
        list.value = [...list.value, ...processDanmaku(data)]
    }
}

watch(list, async () => {
    await nextTick()
    infiniteList.value && infiniteList.value.scrollTo({ behavior: "smooth", top: infiniteList.value.$el.scrollHeight })
})

onMounted(() => {
    document.title = "点歌列表"
    getDanmaku()
})
</script>
<template>
    <el-container class="danmaku-container">
        <el-scrollbar class="danmaku-list" ref="infiniteList">
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
        </el-scrollbar>
    </el-container>
</template>
<route lang="json">
{
    "meta": {
        "layout": "blank"
    }
}
</route>