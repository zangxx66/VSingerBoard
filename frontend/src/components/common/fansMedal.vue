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
    class="mr-5px ml-6px relative v-middle inline-block lh-18px text-12px fans-medal-container"
    title="这是 TA 的粉丝勋章 (●'◡'●)ﾉ♥"
  >
    <div
      class="relative block box-content h-14px lh-14px ws-nowrap font-yahei"
      border="1px solid transparent rd-2px"
      text="white 12px"
      :style="{ borderColor: guard_level === 0 ? medalColor.start : medalBorderColor[guard_level] }"
    >
      <div
        class="flex flex-center float-left box-content min-w-12px h-full lh-14px p-x-4px b-rd-l-1px"
        text="white 12px center ws-nowrap"
        :style="{ backgroundImage: `linear-gradient(45deg,${medalColor.start},${medalColor.end})` }"
      >
        <i
          v-show="props.guard_level !== 0"
          class="block -ml-12px mr-2px w22px h22px"
          bg="no-repeat contain center-center"
        >
          <img class="w-full h-full" :src="props.guard_level === 0 ? '' : `${guardImg}`" alt="" />
        </i>
        <span class="block">{{ props.medal_name }}</span>
      </div>
      <div
        class="block box-content h-full w16px bg-#fff float-left fans-medal-level"
        text="center transparent"
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
}

.fans-medal-level {
  border-top-right-radius: 1px;
  border-bottom-right-radius: 1px;
}
</style>