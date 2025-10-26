<script setup lang="ts">
import { reactive, ref, onMounted } from "vue"
import { CopyDocument } from "@element-plus/icons-vue"
import { ElMessage } from "element-plus"
import { copyToClipboard } from "@/utils"

const formValue = reactive({
    url: `${window.location.origin}/danmaku`
})
const css = ref(`
/* 弹幕列表CSS */
.danmaku-container {
    height: 600px;
    width: 500px;
    background: transparent;
    overflow: hidden;
}
.danmaku-list {
  padding: 0;
  margin-left: 1%;
  list-style: none;
  overflow-y: auto;
}
.danmaku-list-item {
    width: 500px;
    display: flex;
    align-items: center;
    height: 50px;
    text-align: left;
    color: #000;
    font-size: 16px;
    font-weight: bold;
    overflow: hidden;
}
.danmaku-source-img {
    margin: 1px;
    height: 24px;
}
.danmaku-sing {
    width: 200px;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
}

.danmaku-uname {
  width: 180px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  margin-left: 1rem;
}

.fans-club-img {
  margin-left: 10px;
}
.fans-medal-container {
  margin-left: 10px;
}

.danmaku-fans {
  width: 100px;
  margin: 0 auto;
}
/* 弹幕列表CSS END */
`)
const previewData = ref(Array<DanmakuModel>())

const copy = () => {
    copyToClipboard(formValue.url)
    ElMessage.success("拷贝成功")
}

const pushTestData = () => {
    for (let i = 0; i < 10; i++) {
        previewData.value.push({
            uid: i,
            msg: "点歌弹幕",
            uname: "username",
            medal_level: i,
            medal_name: "粉丝团",
            guard_level: 0,
            source: i % 2 == 0 ? "bilibili" : "douyin",
            send_time: Date.now()
        })
    }
}

onMounted(() => {
    pushTestData()
})
</script>
<template>
    <el-card>
        <template #header>
            <span>OBS设置</span>
        </template>
        <div class="obs-container">
            <el-form :model="formValue" label-width="auto">
                <el-form-item label="OBS地址" prop="url">
                    <el-input v-model="formValue.url" type="text" disabled>
                        <template #append>
                            <el-button type="primary" @click="copy">
                                <el-icon>
                                    <CopyDocument />
                                </el-icon>
                            </el-button>
                        </template>
                    </el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="copy">
                        复制地址
                    </el-button>
                </el-form-item>
            </el-form>
            <el-alert title="在OBS新建一个浏览器源，在地址栏输入上面复制的地址，即可实现与观众同步点歌板信息，如需使用自定义css样式，请到下方编辑，然后复制到OBS浏览器源中" :closable="false" type="primary" />
            <div class="obs-splitter">
                <el-splitter>
                    <el-splitter-panel :resizable="false">
                        <div class="css-editor">
                            <line-header title="样式编辑器"></line-header>
                            <el-input v-model="css" :rows="20" type="textarea" placeholder="css样式在这里编辑" />
                        </div>
                    </el-splitter-panel>
                    <el-splitter-panel :resizable="false">
                        <div class="css-editor-preview">
                            <line-header title="样式预览"></line-header>
                            <div class="danmaku-container">
                                <div class="danmaku-list">
                                    <template v-for="item in previewData">
                                        <div class="danmaku-list-item">
                                            <div class="danmaku-sing">
                                                <template v-if="item.html != undefined && item.html.length > 0">
                                                    <el-text v-html="item.html" style="display: flex;"></el-text>
                                                </template>
                                                <template v-else>
                                                    {{ item.msg }}
                                                </template>
                                            </div>
                                            <div class="danmaku-uname">
                                                {{ item.uname }}
                                            </div>
                                            <div class="danmaku-fans">
                                                <template v-if="item.medal_level > 0">
                                                    <template v-if="item.source == 'bilibili'">
                                                        <fans-medal :medal_name="item.medal_name"
                                                            :medal_level="item.medal_level"
                                                            :guard_level="item.guard_level" />
                                                    </template>
                                                    <template v-if="item.source == 'douyin'">
                                                        <fans-club :medal_name="item.medal_name"
                                                            :medal_level="item.medal_level"
                                                            :guard_level="item.guard_level" />
                                                    </template>
                                                </template>
                                            </div>
                                        </div>
                                    </template>
                                </div>
                            </div>
                        </div>
                    </el-splitter-panel>
                </el-splitter>
            </div>
        </div>
    </el-card>
    <component :is="'style'">{{ css }}</component>
</template>
<style scoped>
.css-editor,
.css-editor-preview {
    padding: 1rem;
}
.css-editor-preview .danmaku-container {
    --grid-size: 20px;
    --color-light: #f0f0f0;
    --color-dark: #cccccc;

    background: 
        repeating-conic-gradient(
            var(--color-light) 0% 25%, 
            var(--color-dark) 0% 50%
        );

    background-size: var(--grid-size) var(--grid-size);
}
</style>