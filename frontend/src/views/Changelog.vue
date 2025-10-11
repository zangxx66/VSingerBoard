<script setup lang="ts">
import { reactive, onMounted, resolveComponent, h, render, ref } from "vue"
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

const linkIconComponent = resolveComponent("link-icon")
const initChagngelog = async () => {
    loading.value = true
    const response = await window.pywebview.api.update_verion()
    if (response.code == 0) {
        model.version = response.version
        model.publishedAt = utcToLocal(response.published_at)
        const htmlString = await marked.parse(response.body)
        const container = document.createElement("div")
        render(h(linkIconComponent), container)
        const svgIcon = container.innerHTML
        model.changelog = htmlString
            .replace(/<a href/g, '<a target="_blank" href')
            .replace(/<\/a>/g, `${svgIcon}</a>`)
    } else {
        ElMessage.warning("获取更新日志失败")
    }
    loading.value = false
}

onMounted(() => {
    initChagngelog()
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