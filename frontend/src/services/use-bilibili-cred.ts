import { request } from '@/api'
import { ElMessage } from 'element-plus'

export const useGetBilibiliCredential = () => {
    return useQuery({
        queryKey: [request.getBiliCredentialList.name],
        queryFn: async () => {
            const response = await request.getBiliCredentialList({})
            if (response.code != 0) {
                ElMessage.warning(response.msg || "请求失败")
                return [] as BiliCredentialModel[]
            } else {
                return response.data.rows as BiliCredentialModel[]
            }
        },
        staleTime: 1000 * 10
    })
}
