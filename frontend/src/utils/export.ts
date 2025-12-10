import { Workbook, type Column } from 'exceljs'

/**
 * 导出数据到Excel文件
 * @param columns - 列对象数组。每个列对象应包含列的属性，如header、key、width等。
 * @param data - 要导出到Excel文件的数据对象数组。每个数据对象应包含与列对象中的key匹配的属性。
 * @param filename - 导出Excel文件的文件名。
 */
export const exportExcel = async(columns: Partial<Column>[], data: any[], filename: string) => {
    const workbook = new Workbook()
    const worksheet = workbook.addWorksheet('Sheet1')
    worksheet.columns = columns
    worksheet.addRows(data)
    const buffer = await workbook.xlsx.writeBuffer()
    const blob = new Blob([buffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    })

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
}