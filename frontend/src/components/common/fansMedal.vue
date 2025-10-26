<script setup lang="ts">
import { ref } from "vue"

const props = defineProps<{
    medal_name: string
    medal_level: number
    guard_level: number
}>()

const fansMedalColorMap = [
  [
    (level: number) => level < 1,
    () => ({
      start: '#ffffff',
      end: '#ffffff'
    })
  ],
  [
    (level: number) => level >= 1 && level < 5,
    () => ({
      start: '#5c968e',
      end: '#5c968e',
    }),
  ],
  [
    (level: number) => level >= 5 && level < 9,
    () => ({
      start: '#5d7b9e',
      end: '#5d7b9e',
    }),
  ],
  [
    (level: number) => level >= 9 && level < 13,
    () => ({
      start: '#8d7ca6',
      end: '#8d7ca6',
    }),
  ],
  [
    (level: number) => level >= 13 && level < 17,
    () => ({
      start: '#be6686',
      end: '#be6686',
    }),
  ],
  [
    (level: number) => level >= 17 && level < 21,
    () => ({
      start: '#c79d24',
      end: '#c79d24',
    }),
  ],
  [
    (level: number) => level >= 21 && level < 25,
    () => ({
      start: '#1a544b',
      end: '#529d92',
    }),
  ],
  [
    (level: number) => level >= 25 && level < 29,
    () => ({
      start: '#06154c',
      end: '#6888f1',
    }),
  ],
  [
    (level: number) => level >= 29 && level < 33,
    () => ({
      start: '#2d0855',
      end: '#9d9bff',
    }),
  ],
  [
    (level: number) => level >= 33 && level < 37,
    () => ({
      start: '#7a0423',
      end: '#e986bb',
    }),
  ],
  [
    (level: number) => level >= 37,
    () => ({
      start: '#ff610b',
      end: '#ffd084',
    }),
  ],
]

const getMedalColorByLevel = (level: number): { start: string; end: string } => {
  const result = fansMedalColorMap.find(n => n[0](level)) as any

  return result[1]()
}

const medalBorderColor = ['', '#ffe854', '#ffe854', '#67e8ff']

const medalColor = ref<{ start: string; end: string }>({ start: '', end: '' })
medalColor.value = getMedalColorByLevel(props.medal_level)
const guardImg = `${window.location.origin}/assets/images/guard-${props.guard_level}-0.png`
</script>
<template>
      <div
    class="fans-medal-container"
    title="这是 TA 的粉丝勋章 (●'◡'●)ﾉ♥"
  >
    <div
      class="fans-medal-guard-level"
      :style="{ borderColor: guard_level === 0 ? medalColor.start : medalBorderColor[guard_level] }"
    >
      <div
        class="fans-medal-bg"
        :style="{ backgroundImage: `linear-gradient(45deg,${medalColor.start},${medalColor.end})` }"
      >
        <i
          v-show="props.guard_level !== 0"
          class="fans-medal-guard-img"
        >
          <img style="width: 100%;height: 100%;" :src="props.guard_level === 0 ? '' : `${guardImg}`" alt="" />
        </i>
        <span style="display: block;">{{ props.medal_name }}</span>
      </div>
      <div
        class="fans-medal-level"
        :style="{ color: medalColor.start }"
      >
        {{ props.medal_level }}
      </div>
    </div>
  </div>
</template>
<style scoped>
.fans-medal-container {
  user-select: none;
  margin-right: 5px;
  margin-left: 6px;
  line-height: 18px;
  font-size: 12px;
  position: relative;
  vertical-align: middle;
  display: inline-block;
}

.fans-medal-guard-level {
  position: relative;
  display: block;
  box-sizing: content-box;
  height: 14px;
  line-height: 14px;
  white-space: nowrap;
  border: 1px solid transparent;
  border-radius: 2px;
  color: white;
  font-size: 12px;
}

.fans-medal-bg {
  display: flex;
  align-items: center;
  justify-content: center;
  float: left;
  box-sizing: content-box;
  min-width: 12px;
  height: 100%;
  line-height: 14px;
  padding-left: 4px;
  padding-right: 4px;
  border-top-left-radius: 1px;
  border-bottom-left-radius: 1px;
  color: white;
  font-size: 12px;
  text-align: center;
  white-space: nowrap;
}

.fans-medal-guard-img {
  display: block;
  margin-left: -12px;
  margin-right: 2px;
  width: 22px;
  height: 22px;
  background: no-repeat contain;
  background-position: center center;
}

.fans-medal-level {
  border-top-right-radius: 1px;
  border-bottom-right-radius: 1px;
  float: left;
  box-sizing: content-box;
  display: block;
  height: 100%;
  width: 16px;
  background: #fff;
  text-align: center;
}
</style>