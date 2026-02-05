<script setup lang="ts">
import { request } from "@/api"
import { getNowTimespan } from "@/utils"
import { ElMessage } from "element-plus"

const emit = defineEmits<{
    submit: [result: PlaylistModel]
}>()
const isShow = ref(false)
const loading = ref(false)
const baseFormValue = reactive<PlaylistModel>({
    id: 0,
    song_name: "",
    singer: "",
    is_sc: false,
    sc_price: 0,
    language: "",
    tag: "",
    create_time: 0
})

const openDialog = (model?: PlaylistModel | undefined) => {
    if (model) {
        Object.assign(baseFormValue, model)
    }
    isShow.value = true
}

const closeDialog = () => {
    isShow.value = false
    baseFormValue.id = 0
    baseFormValue.song_name = ""
    baseFormValue.singer = ""
    baseFormValue.is_sc = false
    baseFormValue.sc_price = 0
    baseFormValue.language = ""
    baseFormValue.tag = ""
}

const onSubmit = () => {
    if (!baseFormValue.song_name) {
        ElMessage.warning("请输入歌名")
        return
    }
    if (!baseFormValue.singer) {
        ElMessage.warning("请输入歌手")
        return
    }
    if (baseFormValue.is_sc && !baseFormValue.sc_price) {
        ElMessage.warning("请输入SC价格")
        return
    }
    loading.value = true
    baseFormValue.create_time = getNowTimespan()
    request.addOrUpdatePlaylist({ data: baseFormValue }).then(response => {
        if (response.code != 0) {
            ElMessage.warning(response.msg)
            loading.value = false
            return
        }
        ElMessage.success(response.msg)
        baseFormValue.id = response.data
        const result: PlaylistModel = {
            id: baseFormValue.id,
            song_name: baseFormValue.song_name,
            singer: baseFormValue.singer,
            is_sc: baseFormValue.is_sc,
            sc_price: baseFormValue.sc_price,
            language: baseFormValue.language,
            tag: baseFormValue.tag,
            create_time: baseFormValue.create_time
        }
        emit("submit", result)
        loading.value = false
        closeDialog()
    }).catch(error => {
        ElMessage.error(error)
        loading.value = false
    })
}

defineExpose({ openDialog })
</script>
<template>
    <el-dialog v-model="isShow" title="新增歌曲" width="450" destroy-on-close :before-close="closeDialog">
        <el-form :model="baseFormValue" label-width="auto">
            <el-form-item label="歌名" prop="song_name">
                <el-input v-model="baseFormValue.song_name" type="text" />
            </el-form-item>
            <el-form-item label="歌手" prop="singer">
                <el-input v-model="baseFormValue.singer" type="text" />
            </el-form-item>
            <el-form-item label="语种" prop="language">
                <el-input v-model="baseFormValue.language" type="text" />
            </el-form-item>
            <el-form-item label="标签" prop="tag">
                <el-input v-model="baseFormValue.tag" type="text" />
            </el-form-item>
            <el-form-item label="是否SC歌曲" prop="is_sc">
                <el-radio-group v-model="baseFormValue.is_sc">
                    <el-radio :value="true">是</el-radio>
                    <el-radio :value="false">否</el-radio>
                </el-radio-group>
            </el-form-item>
            <template v-if="baseFormValue.is_sc">
                <el-form-item label="SC价格" prop="sc_price">
                    <el-input-number v-model="baseFormValue.sc_price" :min="30" :controls="false" />
                </el-form-item>
            </template>
            <el-form-item>
                <el-button :loading="loading" type="primary" @click="onSubmit()">保存</el-button>
                <el-button @click="closeDialog()">取消</el-button>
            </el-form-item>
        </el-form>
    </el-dialog>
</template>