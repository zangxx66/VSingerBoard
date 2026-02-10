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
export const timespanToString = (timespan: number) => {
    return dayjs.unix(timespan).format("YYYY-MM-DD HH:mm:ss")
}

/**
 *  获取从给定日期开始的相对时间
 *
 *  @param {string | number} date - 获取相对时间所需的时间点
 *  @param {string} format - 日期的格式
 *  @returns {string} 相对时间
 */
export const getRelativeTime = (date: string | number, format: string): string => {
    return dayjs(date, format).fromNow()
}

/**
 * 将字符串转换为时间戳
 * @param date 字符串,格式为 "YYYY-MM-DD HH:mm:ss"
 * @returns 时间戳
 */
export const getTimespan = (date: string) => {
    return dayjs(date).unix()
}

/**
 * 将 UTC 时间字符串转换为本地时间字符串
 * @param {string} date - UTC 时间字符串,格式为 "YYYY-MM-DD HH:mm:ss"
 * @returns {string} 本地时间字符串,格式为 "YYYY-MM-DD HH:mm:ss"
 */
export const utcToLocal = (date: string): string => {
    return dayjs.utc(date).local().format('YYYY-MM-DD HH:mm:ss')
}


/**
 * 获取当前时间的时间戳
 * @returns {number} 当前时间的时间戳
 */
export const getNowTimespan = (): number => {
    return dayjs().unix()
}

/**
 * 获取当前日期的字符串表示
 * @returns {string} 当前日期的字符串表示，格式为 "YYYY-MM-DD"
 */
export const getNowDateString = (): string => {
    return dayjs().format('YYYY-MM-DD')
}

/**
 * 获取当天时间戳的 23:59:59
 * @param tiemspan 秒级时间戳
 * @returns {number} 转换后的 23:59:59 的时间戳
 */
export const getEndOfDayTimespan = (tiemspan: number): number => {
    return dayjs.unix(tiemspan).endOf("day").unix()
}
