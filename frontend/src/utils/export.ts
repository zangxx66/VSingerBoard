import * as ExcelJS from 'exceljs'

/**
 * Export data to an Excel file
 * @param columns - Array of column objects. Each column object should contain properties for the column such as header, key, width, etc.
 * @param data - Array of data objects to be exported to the Excel file. Each data object should contain properties that match the keys in the column objects.
 * @param filename - The filename of the exported Excel file.
 */
export const exportExcel = async(columns: Partial<ExcelJS.Column>[], data: any[], filename: string) => {
    const workbook = new ExcelJS.Workbook()
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