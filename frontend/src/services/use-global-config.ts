import { ElMessage } from 'element-plus'

export const useGetGlobalConfig = () => {
  return useQuery({
    queryKey: [getGlobalConfig.name],
    queryFn: async () => {
      const response = await getGlobalConfig({})
      if (response.code != 0) {
        ElMessage.warning(response.msg || '获取配置失败')
        return {
          id: 0,
          dark_mode: false,
          check_update: false,
          startup: false,
          notification: false,
          navSideTour: false,
          collapse: false,
        } as GlobalConfigModel
      } else {
        return response.data.data as GlobalConfigModel
      }
    },
    staleTime: 1000 * 10,
    enabled: computed(() => !!window.pywebview),
  })
}
