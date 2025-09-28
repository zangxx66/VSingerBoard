import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 全局定时器 Store
 */
export const useIntervalStore = defineStore('interval', () => {
  const activeIntervals = ref<Record<string, number>>({})

  /**
   * Add a interval to the store.
   * If the key already exists in the store, the existing interval will be cleared.
   * @param {string} key - the key to store the interval under
   * @param {() => void} cb - the callback to execute when the interval fires
   * @param {number} delay - the delay between interval executions in milliseconds
   */
  const addInterval = (key: string, cb: () => void, delay: number) => {
    if(activeIntervals.value[key]) {
      clearInterval(activeIntervals.value[key])
    }
    activeIntervals.value[key] = window.setInterval(cb, delay)
  }


/**
 * Remove an interval from the store by key.
 * If the interval exists in the store, it will be cleared.
 * @param {string} key - the key to remove the interval from
 */
  const removeInterval = (key: string) => {
    if(activeIntervals.value[key]) {
      clearInterval(activeIntervals.value[key])
      delete activeIntervals.value[key]
    }
  }


/**
 * Clears all intervals from the store.
 * This method iterates over all keys in the activeIntervals object and
 * clears the interval associated with each key, then resets the
 * activeIntervals object to an empty object.
 */
  const clearAllIntervals = () => {
    Object.keys(activeIntervals.value).forEach((key) => {
      clearInterval(activeIntervals.value[key])
    })
    activeIntervals.value = {}
  }

  return { activeIntervals, addInterval, removeInterval, clearAllIntervals }
})
