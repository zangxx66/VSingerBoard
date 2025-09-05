import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const timespanToString = (timespan: number) => {
    return dayjs.unix(timespan).format("YYYY-MM-DD HH:mm:ss")
}

const getRelativeTime = (date: string | number, format: string) => {
    return dayjs(date, format).fromNow()
}

const getTimespan = (date: string) => {
    return dayjs(date).unix()
}

export {
    timespanToString,
    getRelativeTime,
    getTimespan
}
