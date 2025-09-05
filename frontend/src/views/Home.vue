<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { request } from "@/api"
import type { ResponseModel, SubscribeModel } from "@/types"

const activeName = ref("1")
const biliSubscribe = ref<SubscribeModel>({
    id: 0,
    room_id: 0,
    source: "bilibili",
    create_time: 0
})
const dySubscribe = ref<SubscribeModel>({
    id: 0,
    room_id: 0,
    source: "douyin",
    create_time: 0
})

const initSub = () => {
    request.getSubscribeList({}).then(response => {
        const resp = response.data as ResponseModel
        if (resp.code != 0) {
            ElMessage.warning(resp.msg)
        } else {
            const list = resp.data.rows as Array<SubscribeModel>
            list.forEach((value, index, array) => {
                if (value.source == "bilibili") {
                    biliSubscribe.value = value
                }
                if (value.source == "douyin") {
                    dySubscribe.value = value
                }
            })

        }
    }).catch(error => ElMessage.error(error))
}

onMounted(() => {
    initSub()
})
</script>
<template>
    <el-container class="home-container">
        <el-main class="home-main">
            <el-card class="home-tab-card">
                <el-tabs v-model="activeName" type="border-card" class="demo-tabs">
                    <el-tab-pane label="直播间设置" name="1">
                        <el-space directions="vertical" :size="20">
                            <el-card class="live-card">
                                <template #header>
                                    <div class="live-header">
                                        <span>Bilibili</span>
                                    </div>
                                </template>
                                <el-form :model="biliSubscribe" label-width="auto">
                                    <el-form-item label="房间号" prop="room_id">
                                        <el-input v-model="biliSubscribe.room_id" placeholder="B站直播间号" type="number" />
                                    </el-form-item>
                                </el-form>
                            </el-card>
                            <el-card class="live-card">
                                <template #header>
                                    <div class="live-header">
                                        <span>抖音</span>
                                    </div>
                                </template>
                                <el-form :model="dySubscribe" label-width="auto">
                                    <el-form-item label="房间号" prop="room_id">
                                        <el-input v-model="dySubscribe.room_id" placeholder="抖音直播间号" type="number" />
                                    </el-form-item>
                                </el-form>
                            </el-card>
                            <el-card class="live-card">
                                <el-button type="primary">保存</el-button>
                            </el-card>
                        </el-space>
                    </el-tab-pane>
                    <el-tab-pane label="点歌设置" name="2" lazy>
                        B站点歌设置
                    </el-tab-pane>
                    <el-tab-pane label="B站账号设置" name="3" lazy>
                        B站账号设置
                    </el-tab-pane>
                </el-tabs>
            </el-card>
        </el-main>
    </el-container>
</template>
<style scoped>
.home-tab-card {
    display: flex;
    justify-content: center;
    /* 水平居中 */
    align-items: center;
    /* 垂直居中 */
}
</style>