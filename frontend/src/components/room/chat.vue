<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from "vue"
import type { DanmakuModel, ResponseModel, BiliConfigModel } from "@/types"
import { ElMessage } from "element-plus"
import { request } from "@/api"
import { CloseBold } from "@element-plus/icons-vue"

const danmakuList = ref(Array<DanmakuModel>())
const config = reactive<BiliConfigModel>({
    id: 0,
    room_id: 0,
    modal_level: 0,
    user_level: 0,
    sing_prefix: '点歌',
    sing_cd: 0
})
const timer = ref(0)

const initConfig = () => {
    request.getBiliConfig({}).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            if (!resp.data.data) return
            const cfg = resp.data.data as BiliConfigModel
            config.id = cfg.id
            config.room_id = cfg.room_id
            config.modal_level = cfg.modal_level
            config.user_level = cfg.user_level
            config.sing_prefix = cfg.sing_prefix
            config.sing_cd = cfg.sing_cd
            wsConnect()
        }
    }).catch(error => ElMessage.error(error))
}

const wsConnect = () => {
    timer.value = setInterval(async () => {
        // @ts-ignore
        const list = await window.pywebview.api.get_danmu() as Array<DanmakuModel>
        if (list) {
            danmakuList.value.push(...list)
        }
        // @ts-ignore
        const dylist = await window.pywebview.api.get_dy_danmu() as Array<DanmakuModel>
        if (dylist) {
            danmakuList.value.push(...dylist)
        }

    }, 1000)
}

const load = () => console.log("load")

const copyToClipboard = (txt: string) => {
    // @ts-ignore
    window.pywebview.api.copy_to_clipboard(txt)
    ElMessage.success("拷贝成功")
}

const close = (danmaku: DanmakuModel) => {
    const newList = danmakuList.value.filter(item => item.uid != danmaku.uid && item.source != danmaku.source)
    danmakuList.value = newList
}

onMounted(() => {
    initConfig()
    // danmakuList.value.push(...[{
    //     uid: 0,
    //     uname: "999",
    //     msg: "string",
    //     send_time: 1,
    //     source: "bilibili"
    // }, {
    //     uid: 0,
    //     uname: "ciruno",
    //     msg: "yayaya",
    //     send_time: 2,
    //     source: "douyin"
    // }])
})

onBeforeUnmount(() => {
    clearInterval(timer.value)
    timer.value = 0
})
</script>
<template>
    <el-container class="chat-container">
        <el-main class="chat-main">
            <el-card class="chat-card">
                <template #header>
                    <div class="card-header">
                        <span>点歌列表</span>
                    </div>
                </template>
                <div class="infinite-list" v-infinite-scroll="load">
                    <template v-for="item in danmakuList">
                        <div class="infinite-list-item">
                            <template v-if="item.source == 'bilibili'">
                                <img src="/assets/images/bilibili.png" class="source-img" alt="bilibili" width="24" />
                            </template>
                            <template v-else-if="item.source == 'douyin'">
                                <img src="/assets/images/douyin.png" class="source-img" alt="douyin" width="24" />
                            </template>
                            <el-text tag="span" class="chat-tag" @click="copyToClipboard(item.msg)">
                                {{ item.uname }}：{{ item.msg }}
                            </el-text>
                            <el-text tag="span" class="chat-close" @click="close(item)">
                                <el-icon>
                                    <CloseBold />
                                </el-icon>
                            </el-text>
                        </div>
                    </template>
                </div>
            </el-card>
        </el-main>
    </el-container>
</template>
<style scoped>
.chat-main {
    height: calc(100vh - 60px);
}

.chat-card {
    height: 100%;
}

.infinite-list {
    height: 70%;
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

</style>