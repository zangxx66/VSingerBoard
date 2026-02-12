import { ElMessage } from 'element-plus'

export const useGetHistoryInfinite = (params: RequestHistory) => {
  return useInfiniteQuery({
    queryKey: [getHistoryList.name, params] as const,
    queryFn: async (args) => {
      const response = await getHistoryList({ ...args.queryKey[1], page: args.pageParam })
      if (response.code != 0) {
        ElMessage.warning(response.msg || '请求失败')
        return { total: 0, rows: [] }
      } else {
        return {
          total: response.data.total as number,
          rows: response.data.rows as ResponseHistory[],
        }
      }
    },
    getNextPageParam: (lastPage, pages) => {
      const size = unref(unref(params).size) ?? 20
      return lastPage.total >= size ? pages.length + 1 : undefined
    },
    staleTime: 1000 * 10,
    initialPageParam: 1,
  })
}
