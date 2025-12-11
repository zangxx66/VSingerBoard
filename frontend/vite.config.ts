import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
    AutoImport({
      imports: ['vue', 'pinia', 'vue-router', '@vueuse/core'],
      dirs: ['./src/stores/**'],
      resolvers: [
        ElementPlusResolver(),
        IconsResolver({
          prefix: 'Icon',
        }),
      ],
    }),
    Components({
      extensions: ['vue', 'tsx'],
      include: [/\.vue$/, /\.vue\?vue/, /\.tsx$/],
      resolvers: [
        IconsResolver({
          enabledCollections: ['ep'],
        }),
        ElementPlusResolver(),
      ],
    }),
    Icons({
      autoInstall: true,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
  },
  build: {
    outDir: '../wwwroot',
    minify: 'terser',
    reportCompressedSize: false,
    rollupOptions: {
      output: {
        chunkFileNames: 'assets/[name]-[hash].js',
        manualChunks(id: string) {
          if (id.includes('node_modules/.pnpm/')) {
            const matched = id.match(/node_modules\/\.pnpm\/([^/]+)\/node_modules\/([^/]+)/)

            if (matched && matched.length > 2) {
              const pkgName = matched[2]
              if (['vue', 'vue-router', 'pinia', '@vueuse'].includes(pkgName)) {
                return 'vendor-vue'
              }
              if (['element-plus', '@element-plus'].includes(pkgName)) {
                return 'vendor-element-plus'
              }
              if (['marked', 'marked-highlight'].includes(pkgName)) {
                return 'vendor-marked'
              }
              if (pkgName === 'highlight.js') {
                return 'vendor-highlight-js'
              }
              if (pkgName === 'exceljs') {
                return 'vendor-exceljs'
              }
              return 'vendor-libs'
            }
          }
          if (id.includes('node_modules')) {
            return 'vendor-libs'
          }
        },
      },
    },
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
})
