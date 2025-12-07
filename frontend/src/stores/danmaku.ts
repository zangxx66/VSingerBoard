import { defineStore } from "pinia"

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

    const clearDanmakuList = (source?: string) => {
        danmakuList.value = source && source.length > 0 ? danmakuList.value.filter(item => item.source != source) : []
    }

    const removeDanmakuList = (danmaku: DanmakuModel) => {
        const index = danmakuList.value.indexOf(danmaku)
        if(index > -1){
            danmakuList.value.splice(index, 1)
        }
    }

    const updateDanmakuStatus = (msg_id: number, status: number) => {
        const danmaku = danmakuList.value.find(item => item.msg_id == msg_id)
        if(danmaku) {
            danmaku.status = status
        }
    }

    return {
        danmakuList,
        getDanmakuList,
        setDanmakuList,
        pushDanmakuList,
        clearDanmakuList,
        removeDanmakuList,
        updateDanmakuStatus,
    }
})