import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 全局定时器 Store
 */
export const useIntervalStore = defineStore('interval', () => {
  const activeIntervals = ref<Record<string, number>>({})

  /**
   * 向store中添加一个定时器。
   * 如果key已存在于store中，则现有定时器将被清除。
   * @param {string} key - 存储定时器的键
   * @param {() => void} cb - 定时器触发时执行的回调函数
   * @param {number} delay - 定时器执行之间的延迟（毫秒）
   */
  const addInterval = (key: string, cb: () => void, delay: number) => {
    if(activeIntervals.value[key]) {
      clearInterval(activeIntervals.value[key])
    }
    activeIntervals.value[key] = window.setInterval(cb, delay)
  }


/**
 * 根据key从store中移除一个定时器。
 * 如果定时器存在于store中，它将被清除。
 * @param {string} key - 要移除的定时器的键
 */
  const removeInterval = (key: string) => {
    if(activeIntervals.value[key]) {
      clearInterval(activeIntervals.value[key])
      delete activeIntervals.value[key]
    }
  }


/**
 * 清除store中的所有定时器。
 * 此方法遍历activeIntervals对象中的所有键，
 * 清除与每个键关联的定时器，然后将activeIntervals对象重置为空对象。
 */
  const clearAllIntervals = () => {
    Object.keys(activeIntervals.value).forEach((key) => {
      clearInterval(activeIntervals.value[key])
    })
    activeIntervals.value = {}
  }

  return { activeIntervals, addInterval, removeInterval, clearAllIntervals }
})
