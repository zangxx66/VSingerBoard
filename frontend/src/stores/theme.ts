import { defineStore } from "pinia"
import { reactive } from 'vue'
import { request } from "@/api"
import { ElMessage } from "element-plus"
import { toggleDark } from "@/utils"

export const useThemeStore = defineStore('theme', () => {
    const globalCfg = reactive({
        id: 0,
        dark_mode: false,
    })

    const getDarkTheme = () => {
        return globalCfg.dark_mode
    }

    const setDarkTheme = (id: number, value: boolean) => {
        globalCfg.id = id
        if(value != globalCfg.dark_mode){
            updateConfig(value)
        }
    }

    const updateConfig = (mode: boolean) => {
        request.addOrUpdateGlobalConfig({data: { id: globalCfg.id, dark_mode: mode }}).then(response => {
            const resp = response.data as ResponseModel
            if(resp.code != 0){
                ElMessage.warning(resp.msg)
                return
            }
            globalCfg.dark_mode = mode
            toggleDark(mode)
            return request.getGlobalConfig({})

        })
        .then(response => {
            const resp = response!.data as ResponseModel
            if (resp.code == 0 && globalCfg.id == 0){
                globalCfg.id = (resp.data.data as GlobalConfigModel).id
            }
        })
        .catch(error => ElMessage.error(error))
    }

    return { globalCfg, getDarkTheme, setDarkTheme, updateConfig }
})