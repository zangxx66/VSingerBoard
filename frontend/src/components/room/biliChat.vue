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
    setInterval(async () => {
        // @ts-ignore
        const list = await window.pywebview.api.get_danmu() as Array<DanmakuModel>
        if (list) {
            list.forEach((value, index, array) => {
                if (config.user_level == 0 && value.medal_level >= config.modal_level) {
                    danmakuList.value.push(value)
                }
                if (config.user_level != 0 && value.guard_level <= config.user_level) {
                    danmakuList.value.push(value)
                }
            })
        }

    }, 1000)
}

const load = () => console.log("load")

const copyToClipboard = async (txt: string) => {
    await navigator.clipboard.writeText(txt)
    ElMessage.success("复制成功")
}

onMounted(() => {
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
                        <div class="infinite-list-item" @click="copyToClipboard(item.msg)">
                            <el-text tag="span" class="chat-tag">
                                <el-tag type="primary" v-if="item.medal_level > 0">{{ item.medal_name }} Lv{{ item.medal_level }}</el-tag>
                                {{ item.uname }}：{{ item.msg }}
                            </el-text>
                            <el-text tag="span" class="chat-close">
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

.infinite-list .infinite-list-item {
    display: flex;
    align-items: center;
    justify-content: left;
    height: 50px;
    background: var(--el-color-primary-light-9);
    margin: 10px;
    color: var(--el-color-primary);
    cursor: pointer;

}

.infinite-list .infinite-list-item+.list-item {
    margin-top: 10px;
}

.song-name {
    margin-left: 10px;
}
</style>