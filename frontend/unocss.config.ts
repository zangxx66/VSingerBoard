import { defineConfig, presetAttributify, presetUno, presetIcons } from 'unocss'

export default defineConfig({
  exclude: [
    'node_modules',
    'dist',
    '.git',
    '.husky',
    '.vscode',
    'public',
    'build',
    'mock',
    './stats.html',
  ],
  shortcuts: [
    {
      'flex-center': 'flex justify-center items-center',
    },
  ],
  rules: [
    [
      'font-yahei',
      { 'font-family': '"Inter","Helvetica Neue","Helvetica","PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑","Arial",sans-serif"' },
    ],
  ],
  theme: {},
  presets: [presetUno(), presetIcons(), presetAttributify()],
})