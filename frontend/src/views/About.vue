<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { checkUpdate } from "@/utils"
import { useThemeStore } from "@/stores"

const version = ref("")
const themeStore = useThemeStore()

const getVersion = async() =>{
    version.value = await window.pywebview.api.get_version()
} 

const openGithub = () => {
    const a = document.createElement("a")
    a.href = "https://github.com/zangxx66/VSingerBoard"
    a.target = "_blank"
    a.click()
    a.remove()
}

const openHomepage = () => {
    const a = document.createElement("a")
    a.href = "https://space.bilibili.com/909267"
    a.target = "_blank"
    a.click()
    a.remove()
}

const openIssues = () => {
    const a = document.createElement("a")
    a.href = "https://github.com/zangxx66/VSingerBoard/issues"
    a.target = "_blank"
    a.click()
    a.remove()
}

const isDarktheme = computed(() => {
  return themeStore.getDarkTheme()
})

onMounted(() => {
    getVersion()
})

</script>
<template>
        <el-card>
        <template #header>
            <div class="card-header">
                <span>关于</span>
            </div>
        </template>
        <div class="about-container">
            <template v-if="isDarktheme">
                <img src="/assets/images/logo_night.png" alt="logo" class="about-logo" width="70" />
            </template>
            <template v-else>
                <img src="/assets/images/logo.png" alt="logo" class="about-logo" width="70" />
            </template>
            <div class="about-title">点歌姬</div>
            <div class="about-version">
                v{{ version }}
                <el-button type="primary" @click="checkUpdate" plain>检查更新</el-button>
            </div>
            <div class="about-author-container">
                <el-button color="#909399" @click="openGithub" plain>GitHub仓库</el-button>
                <el-button color="#F56C6C" @click="openHomepage" plain>作者主页</el-button>
                <el-button color="#67C23A" @click="openIssues" plain>问题反馈</el-button>
            </div>
        </div>
    </el-card>
</template>
