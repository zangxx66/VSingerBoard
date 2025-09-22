import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(relativeTime)
dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.locale('zh-cn')

/**
 * 将时间戳转换为字符串
 * @param timespan 时间戳
 * @returns 字符串,格式为 "YYYY-MM-DD HH:mm:ss"
 */
const timespanToString = (timespan: number) => {
    return dayjs.unix(timespan).format("YYYY-MM-DD HH:mm:ss")
}

/**
 *  Gets the relative time from the given date.
 *
 *  @param {string | number} date - The date to get the relative time from.
 *  @param {string} format - The format of the date.
 *  @returns {string} The relative time.
 */
const getRelativeTime = (date: string | number, format: string): string => {
    return dayjs(date, format).fromNow()
}

/**
 * 将字符串转换为时间戳
 * @param date 字符串,格式为 "YYYY-MM-DD HH:mm:ss"
 * @returns 时间戳
 */
const getTimespan = (date: string) => {
    return dayjs(date).unix()
}

/**
 * 将 UTC 时间字符串转换为本地时间字符串
 * @param {string} date - UTC 时间字符串,格式为 "YYYY-MM-DD HH:mm:ss"
 * @returns {string} 本地时间字符串,格式为 "YYYY-MM-DD HH:mm:ss"
 */
const utcToLocal = (date: string) => {
    return dayjs.utc(date).local().format('YYYY-MM-DD HH:mm:ss')
}

export {
    timespanToString,
    getRelativeTime,
    getTimespan,
    utcToLocal
}
