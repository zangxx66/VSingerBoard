import { defineStore } from 'pinia'
import { ref } from 'vue'

// 定义回调对象的类型
type IntervalCallbacks = {
  [key: string]: () => void;
}

/**
 * 全局定时器 Store
 */
export const useIntervalStore = defineStore('interval', () => {
  const intervalId = ref<number | null>(null)
  // 使用对象来存储回调，键是唯一的标识符
  const callbacks = ref<IntervalCallbacks>({})

  /**
   * 启动定时器
   * @param {number} delay 间隔时间 (毫秒)
   */
  const start = (delay: number) => {
    if (intervalId.value) {
      stop()
    }
    intervalId.value = window.setInterval(() => {
      Object.values(callbacks.value).forEach(cb => cb())
    }, delay)
  }

  /**
   * 停止定时器
   */
  const stop = () => {
    if (intervalId.value) {
      window.clearInterval(intervalId.value)
      intervalId.value = null
    }
  }

  /**
   * 添加或更新一个带唯一键的回调函数
   * @param {string} key 唯一键，例如组件名
   * @param {() => void} cb 回调函数
   */
  const addCallback = (key: string, cb: () => void) => {
    callbacks.value[key] = cb
  }

  /**
   * 根据键移除回调函数
   * @param {string} key 唯一键
   */
  const removeCallback = (key: string) => {
    if (callbacks.value[key]) {
      delete callbacks.value[key]
    }
  }

  /**
   * 停止定时器并清空所有回调
   */
  const stopAndClear = () => {
    stop()
    callbacks.value = {}
  }

  return { intervalId, start, stop, addCallback, removeCallback, stopAndClear }
})
