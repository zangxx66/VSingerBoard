import { defineStore } from "pinia"
import { ref } from "vue"

export const useDanmakuStore = defineStore("danmaku", () => {
    const danmakuList = ref(Array<DanmakuModel>())

    const getDanmakuList = () => {
        return danmakuList.value
    }

    const setDanmakuList = (list: DanmakuModel[]) => {
        danmakuList.value = list
    }

    const pushDanmakuList = (list: DanmakuModel[]) => {
        danmakuList.value.push(...list)
    }

    const clearDanmakuList = () => {
        danmakuList.value = []
    }

    const removeDanmakuList = (danmaku: DanmakuModel) => {
        const index = danmakuList.value.indexOf(danmaku)
        if(index > -1){
            danmakuList.value.splice(index, 1)
        }
    }

    return {
        danmakuList,
        getDanmakuList,
        setDanmakuList,
        pushDanmakuList,
        clearDanmakuList,
        removeDanmakuList,
    }
})