<script setup lang="ts">
import { render } from 'vue'
import { Marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'

defineOptions({
  name: 'changelog',
})

const marked = new Marked(
  markedHighlight({
    emptyLangClass: 'hljs',
    langPrefix: '',
    highlight(code, lang, _info) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language }).value
    },
  }),
)

const linkIconComponent = resolveComponent('link-icon')

const {data: response, isFetching } = useGetUpdate()
const model = computedAsync(async () => {
  if (response.value?.code == -2) {
    return response.value
  } else {
    const res = {} as UpdateModel
    Object.assign(res, response.value)
    res.published_at = utcToLocal(res.published_at)
    const htmlString = await marked.parse(res.body)
    const container = document.createElement("div")
    render(h(linkIconComponent), container)
    const svgIcon = container.innerHTML
    const html = htmlString.replace(/<a href/g, '<a target="_blank" href').replace(/<\/a>/g, `${svgIcon}</a>`)
    res.msg = processHTML(html)
    
    return res
  }
})

</script>
<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <line-header class="items-center flex" title="更新日志" />
      </div>
    </template>
    <div v-loading="isFetching" class="changelog-container">
      <h3>{{ model?.version }}</h3>
      <p>{{ model?.published_at }}</p>
      <div class="md-content">
        <div v-html="model?.msg"></div>
      </div>
    </div>
  </el-card>
</template>
<route lang="json">
{
  "name": "changelog"
}
</route>
