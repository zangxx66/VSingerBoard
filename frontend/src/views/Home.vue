<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from "vue"
import { ElMessage } from "element-plus"
import { request } from "@/api"
import { CloseBold } from "@element-plus/icons-vue"
import { emoticons } from "@/utils"

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
// emoji表情
const emojiexp = /\[[\u4E00-\u9FA5A-Za-z0-9_]+\]/g

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
            list.forEach(item => {
                let result = item.msg
                // 替换 emoji
                const matchList = item.msg.match(emojiexp)
                if(matchList){
                    for (const value of matchList) {
                        const emoji = emoticons.find((item) => value === item.emoji)
                        if (emoji) {
                            // 使用全局替换，防止同一个 emoji 多次出现只替换一次
                            result = result.replaceAll(
                                value,
                                `<img src="${emoji.url}" referrerpolicy="no-referrer" width="20" />`,
                            )
                        }
                    }
                    item.html = `${item.uname}： ${result}`
                }
            })
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
    const dom = document.querySelector(".chat-main") as HTMLElement
    dom.style.height = (window.innerHeight - 100) + "px"

    initConfig()
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
                                <template v-if="item.html != undefined">
                                    <el-text v-html="item.html"></el-text>
                                </template>
                                <template v-else>
                                    {{ item.uname }}： {{ item.msg }}
                                </template>
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