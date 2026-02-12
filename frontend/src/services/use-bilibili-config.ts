import { ElMessage } from 'element-plus'

export const useGetBilibiliConfig = () => {
  return useQuery({
    queryKey: [getBiliConfig.name],
    queryFn: async () => {
      const response = await getBiliConfig({})
      if (response.code != 0) {
        ElMessage.warning(response.msg || '请求失败')
        return {
          id: 0,
          room_id: 0,
          modal_level: 1,
          user_level: 0,
          sing_prefix: '点歌',
          sing_cd: 0,
        } as BiliConfigModel
      } else {
        return response.data.data as BiliConfigModel
      }
    },
  })
}
