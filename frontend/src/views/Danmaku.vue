<script setup lang="ts">
import { ref, onMounted } from "vue"
import { processDanmaku } from "@/utils"
import { useWebSocket } from "@vueuse/core"

const list = ref(Array<DanmakuModel>())

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
            if(event.data.startsWith("Echo")){
                return
            }else{
                const value = JSON.parse(event.data) as Array<DanmakuModel>
                const douyin = value.filter(item => item.source == "douyin")
                const bilibili = value.filter(item => item.source == "bilibili")
                list.value = [...list.value, ...processDanmaku(douyin, "douyin"), ...processDanmaku(bilibili, "bilibili")]
            }
        }
    })
}

onMounted(() => {
    getDanmaku()
})
</script>
<template>
    <div class="danmaku-container" v-infinite-scroll="load">
        <template v-for="item in list">
            <div class="danmaku-item">
                <template v-if="item.source == 'bilibili'">
                    <img src="/assets/images/bilibili.png" class="danmaku-source-img" alt="bilibili" width="24" />
                </template>
                <template v-else-if="item.source == 'douyin'">
                    <img src="/assets/images/douyin.png" class="danmaku-source-img" alt="douyin" width="24" />
                </template>
                <el-text tag="span" class="danmaku-tag">
                    <template v-if="item.html != undefined">
                        <el-text v-html="item.html" style="display: flex;"></el-text>
                    </template>
                    <template v-else>
                        {{ item.msg }}
                    </template>
                    {{ item.uname }}
                </el-text>
            </div>
        </template>
    </div>
</template>