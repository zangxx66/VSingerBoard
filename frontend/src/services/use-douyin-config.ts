import { ElMessage } from 'element-plus'

export const useGetDouyinConfig = () => {
  return useQuery({
    queryKey: [getDyConfig.name],
    queryFn: async () => {
      const response = await getDyConfig({})
      if (response.code != 0) {
        ElMessage.warning(response.msg || '请求失败')
        return {
          id: 0,
          room_id: 0,
          sing_prefix: '点歌',
          sing_cd: 0,
          fans_level: 1,
        } as DyConfigModel
      } else {
        return response.data.data as DyConfigModel
      }
    },
  })
}
