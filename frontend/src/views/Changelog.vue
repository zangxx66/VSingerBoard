<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { utcToLocal } from "@/utils"
import { Marked } from "marked"
import { markedHighlight } from "marked-highlight"
import hljs from "highlight.js"

const model = reactive({
    version: "",
    publishedAt: "",
    changelog: ""
})
const loading = ref(false)
const marked = new Marked(
    markedHighlight({
        emptyLangClass: "hljs",
        langPrefix: "",
        highlight(code, lang, info) {
            const language = hljs.getLanguage(lang) ? lang : "plaintext"
            return hljs.highlight(code, { language }).value
        }
    })
)


onMounted(async() => {
    loading.value = true
    const response = await window.pywebview.api.update_verion()
    if(response.code == 0){
        model.version = response.version
        model.publishedAt = utcToLocal(response.published_at)
        const htmlString = await marked.parse(response.body)
        const svgIcon = '<svg viewBox="0 0 24 24" width="1.2em" height="1.2em" class="link-icon" style="display: inline-block; vertical-align: middle; margin-left: 3px;"><path fill="currentColor" d="M10 6v2H5v11h11v-5h2v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6zm11-3v8h-2V6.413l-7.793 7.794l-1.414-1.414L17.585 5H13V3h8z"></path></svg>';
        model.changelog = htmlString
            .replace(/<a href/g, '<a target="_blank" href')
            .replace(/<\/a>/g, `${svgIcon}</a>`)
    }else{
        ElMessage.warning("获取更新日志失败")
    }
    loading.value = false
})
</script>
<template>
    <el-card>
        <template #header>
            <div class="card-header">
                <span>更新日志</span>
            </div>
        </template>
        <div class="changelog-container" v-loading="loading">
            <h3>{{ model.version }}</h3>
            <p>{{ model.publishedAt }}</p>
            <div class="md-content" v-html="model.changelog"></div>
        </div>
    </el-card>
</template>