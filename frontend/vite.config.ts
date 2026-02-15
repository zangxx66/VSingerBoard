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
import VueRouter from 'vue-router/vite'
import { VueRouterAutoImports } from 'unplugin-vue-router'
import Layouts from 'vite-plugin-vue-layouts'
import UnoCSS from 'unocss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    UnoCSS({
      configFile: './uno.config.ts'
    }),
    Layouts({
      layoutsDirs: 'src/layouts',
      defaultLayout: 'default',
      importMode: (_name) => 'async',
    }),
    vueDevTools(),
    AutoImport({
      imports: [
        'vue',
        'pinia',
        VueRouterAutoImports,
        '@vueuse/core',
        { '@tanstack/vue-query': ['useMutation', 'useQuery', 'useInfiniteQuery', 'useQueryClient'] },
      ],
      dirs: ['./src/stores/**', './src/services/**', './src/utils/**', './src/api/index.ts'],
      eslintrc: { enabled: true },
      resolvers: [
        ElementPlusResolver(),
        IconsResolver({
          prefix: 'Icon',
        }),
      ],
      vueTemplate: true
    }),
    VueRouter({
      dts: 'src/route-map.d.ts',
    }),
    Components({
      extensions: ['vue', 'tsx'],
      dirs: ['src/components'],
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
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const assetsName = assetInfo.names[0]
          if (assetsName.endsWith('.css')) {
            return 'css/[name]-[hash].css'
          }

          const imgExts = ['.png', '.jpeg', '.jpg', '.gif', '.svg', '.webp']
          if (imgExts.some((ext) => assetsName.endsWith(ext))) {
            return 'images/[name].[ext]'
          }

          return 'assets/[name]-[hash].[ext]'
        },
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
