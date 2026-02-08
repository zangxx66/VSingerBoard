export default defineComponent({
  name: 'fansMedal',
  props: {
    medal_name: {
      type: String,
      required: true,
    },
    medal_level: {
      type: Number,
      required: true,
    },
    guard_level: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const fansMedalColorMap = [
      [
        (level: number) => level < 1,
        () => ({
          start: '#ffffff',
          end: '#ffffff',
        }),
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
      const result = fansMedalColorMap.find((n) => n[0](level)) as any

      return result[1]()
    }

    const medalBorderColor = ['', '#ffe854', '#ffe854', '#67e8ff']

    const medalColor = ref<{ start: string; end: string }>({ start: '', end: '' })
    medalColor.value = getMedalColorByLevel(props.medal_level)
    const guardImg = `${window.location.origin}/images/guard-${props.guard_level}-0.png`

    const dynamicGuardStyle = {
        borderColor: props.guard_level === 0 ? medalColor.value.start : medalBorderColor[props.guard_level]
    }
    const dynamicBgStyle = {
        backgroundImage: `linear-gradient(45deg,${medalColor.value.start},${medalColor.value.end})`
    }
    const dynamicLevelStyle = {
        color: medalColor.value.start
    }
    const dynamicLevelBg = props.guard_level === 0 ? '' : `${guardImg}`

    return () => (
      <>
        <div class="fans-medal-container" title="这是 TA 的粉丝勋章 (●'◡'●)ﾉ♥">
          <div
            class="fans-medal-guard-level"
            style={dynamicGuardStyle}
          >
            <div
              class="fans-medal-bg"
              style={dynamicBgStyle}
            >
              <i v-show={props.guard_level !== 0} class="fans-medal-guard-img">
                <img
                  style="width: 100%;height: 100%;"
                  src={dynamicLevelBg}
                  alt=""
                />
              </i>
              <span style="display: block;">{props.medal_name}</span>
            </div>
            <div class="fans-medal-level" style={dynamicLevelStyle}>
              {props.medal_level}
            </div>
          </div>
        </div>
      </>
    )
  },
})
