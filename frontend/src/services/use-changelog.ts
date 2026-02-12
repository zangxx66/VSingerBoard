import { ElMessage } from 'element-plus'

export const useGetUpdate = () => {
    return useQuery({
        queryKey: [checkUpdate.name],
        queryFn: async () => {
            const response = await checkUpdate({})
            if(response.code != 0) {
                ElMessage.warning(response.msg || "请求失败")
                return { code: -2, version: "", url: "", body: "", published_at: getNowTimespan(), msg: response.msg || "请求失败" }
            } else {
                return response.data as UpdateModel
            }
        }
    })
}