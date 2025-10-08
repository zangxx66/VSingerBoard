import { defineStore } from "pinia"
import { reactive } from 'vue'

export const useThemeStore = defineStore('theme', () => {
    const globalCfg = reactive({
        id: 0,
        dark_mode: false,
    })

    const getDarkTheme = () => {
        return globalCfg.dark_mode
    }

    const setDarkTheme = (value: boolean) => {
        globalCfg.dark_mode = value
    }

    return { globalCfg, getDarkTheme, setDarkTheme }
})