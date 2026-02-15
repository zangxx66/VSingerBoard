<script setup lang="ts">
import { ElMessage } from "element-plus"

const isShow = ref(false)
const danmakuStore = useDanmakuStore()
const formValue = reactive<DanmakuModel>({
    msg_id: 0,
    uid: 0,
    uname: "",
    msg: "",
    send_time: 0,
    source: "douyin",
    medal_level: 0,
    medal_name: "",
    guard_level: 0
})
const platform = [
    {
        key: "抖音",
        value: "douyin"
    },
    {
        key: "B站",
        value: "bilibili"
    }
]

const openDialog = () => {
    isShow.value = true
}

const closeDialog = () => {
    formValue.uname = ""
    formValue.msg = ""
    formValue.source = "douyin"
}

const submit = () => {
    if (formValue.msg == "") {
        ElMessage.error("点歌内容不能为空")
        return
    }

    formValue.msg_id = getNowTimespan()
    formValue.send_time = getNowTimespan()

    danmakuStore.pushDanmakuList([{...formValue}])
    isShow.value = false
}

defineExpose({ openDialog })
</script>
<template>
    <el-dialog v-model="isShow" title="手动点歌" width="480" destroy-on-close @close="closeDialog">
        <el-form :model="formValue" label-width="auto">
            <el-form-item label="用户昵称" prop="uname">
                <el-input v-model="formValue.uname" placeholder="用户昵称" type="text" />
            </el-form-item>
            <el-form-item label="点歌内容" prop="msg">
                <el-input v-model="formValue.msg" placeholder="点歌内容" type="text" />
            </el-form-item>
            <el-form-item label="点歌平台" prop="source">
                <el-select v-model="formValue.source" placeholder="请选择点歌平台">
                    <template v-for="(item, index) in platform" :key="index">
                        <el-option :label="item.key" :value="item.value" />
                    </template>
                </el-select>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submit()">保存</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>
