import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useContextMenuStore = defineStore('contextmenu', () => {
    const theme = ref<string>("mac")

    const getTheme = () => {
        return theme.value
    }

    const setTheme = (value: string) => {
        theme.value = value
    }

    return { theme, getTheme, setTheme }
})