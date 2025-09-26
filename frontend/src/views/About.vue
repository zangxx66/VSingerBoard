<script setup lang="ts">
import { ref, onMounted } from "vue"
import { checkUpdate } from "@/utils"

const version = ref("")

const getVersion = async() =>{
    version.value = await window.pywebview.api.get_version()
} 

const openGithub = () => {
    const a = document.createElement("a")
    a.href = "https://github.com/zangxx66/VSingerBoard"
    a.target = "_blank"
    a.click()
}

const openHomepage = () => {
    const a = document.createElement("a")
    a.href = "https://space.bilibili.com/909267"
    a.target = "_blank"
    a.click()
}

const openIssues = () => {
    const a = document.createElement("a")
    a.href = "https://github.com/zangxx66/VSingerBoard/issues"
    a.target = "_blank"
    a.click()
}

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
            <img src="/assets/images/logo.png" alt="logo" class="about-logo" width="70" />
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
<style scoped>
.about-container {
    position: relative;
    display: block;
}

.about-logo {
    margin: 0 auto;
    display: block;
    width: 200px;
    height: 100px;
}

.about-title {
    margin: 0 auto;
    display: block;
    text-align: center;
    width: 200px;
    height: 20px;
    font-size: x-large;
}

.about-version {
    margin: 0 auto;
    margin-top: 3%;
    display: block;
    text-align: center;
    width: 200px;
    height: 20px;
}

.about-author-container {
    margin: 0 auto;
    margin-top: 3%;
    display: flex;
    justify-content: center;
}
</style>