import { Workbook, type Column } from 'exceljs'

const ConvertCellValue = (cell: any, cellType: string) => {
  if (!cell || !cellType) return cell

  switch (cellType) {
    case 'string':
      return String(cell)
    case 'number': {
      const num = Number(cell)
      return isNaN(num) ? cell : num
    }
    case 'boolean': {
      if ('boolean' === typeof cell) return cell
      const lowerString = String(cell).toLowerCase()
      if (lowerString === 'true' || lowerString === '1' || lowerString === '是') {
        return true
      }
      if (lowerString === 'false' || lowerString === '0' || lowerString === '否') {
        return false
      }
      return Boolean(cell)
    }
    default:
      return cell
  }
}

/**
 * 导出数据到Excel文件
 * @param columns - 列对象数组。每个列对象应包含列的属性，如header、key、width等。
 * @param data - 要导出到Excel文件的数据对象数组。每个数据对象应包含与列对象中的key匹配的属性。
 * @param filename - 导出Excel文件的文件名。
 */
export const exportExcel = async (columns: Partial<Column>[], data: any[], filename: string) => {
  const workbook = new Workbook()
  const worksheet = workbook.addWorksheet('Sheet1')
  worksheet.columns = columns
  worksheet.addRows(data)
  const buffer = await workbook.xlsx.writeBuffer()
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
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

/**
 * 导入Excel文件，返回对应的数据模型数组
 * @param columns 列对象数组，每个列对象应包含列的属性。
 * @param buffer 用户上传文件的ArrayBuffer对象
 * @returns Array<T>
 */
export const importExcel = async <T>(
  columns: Partial<ImportColumn>[],
  buffer?: ArrayBuffer,
): Promise<Array<T>> => {
  if (!buffer) {
    return []
  }

  const workbook = new Workbook()
  try {
    const loadedWorkbook = await workbook.xlsx.load(buffer)
    const worksheet = loadedWorkbook.getWorksheet(1)

    if (!worksheet) {
      return []
    }

    const result: Array<T> = []
    let headers: string[] = []

    worksheet.eachRow((row, rowNumber) => {
      const values = row.values as any[]

      if (rowNumber === 1) {
        headers = values.slice(1).map((cell) => (cell ? String(cell) : ''))
        return
      }

      const rowObject: DynamicObject = {}
      const rowValues = values.slice(1)

      rowValues.forEach((value, indexInSlicedValues) => {
        const header = headers[indexInSlicedValues]
        if (header) {
          const columnDef = columns.find((item) => item.header === header)
          if (columnDef && columnDef.key) {
            const cellValue = ConvertCellValue(value, columnDef.type!)
            rowObject[columnDef.key as string] = cellValue
          }
        }
      })

      result.push(rowObject as T)
    })

    return result
  } catch (error) {
    console.error('Failed to import Excel file:', error)
    throw error
  }
}
