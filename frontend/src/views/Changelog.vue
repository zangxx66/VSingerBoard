<script setup lang="ts">
import { ref, onMounted, computed, h } from "vue"
import { ElMessage } from "element-plus"
import { utcToLocal } from "@/utils"
import { marked } from "marked"

const version = ref("")
const publishedAt = ref("")
const changelog = ref("")
const loading = ref(false)
const regx = /<a[^>]*>|<\/a>/g

const changelogHtml = computed(() => {
    if (changelog.value) {
        let html = marked.parse(changelog.value) as string
        html = html.replace(regx, "")
        return html
    }
    return ""
})

onMounted(async() => {
    loading.value = true
    const response = await window.pywebview.api.check_for_updates()
    if(response.code == 0){
        version.value = response.version
        publishedAt.value = utcToLocal(response.published_at)
        changelog.value = response.body
    }else{
        ElMessage.warning("获取更新日志失败")
    }
    loading.value = false
})
</script>
<template>
    <el-card v-loading="loading">
        <template #header>
            <div class="card-header">
                <span>更新日志</span>
            </div>
        </template>
        <div class="changelog-container">
            <h3>{{ version }}</h3>
            <p>{{ publishedAt }}</p>
            <div class="md-content" v-html="changelogHtml">
            </div>
        </div>
    </el-card>
</template>