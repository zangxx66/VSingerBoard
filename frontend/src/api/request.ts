import { client } from "./client"
import type { AxiosResponse } from "axios"

class Request {
    /**
     * 获取Bilibili配置。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 获取操作的响应。
     */
    async getBiliConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_bili_config", params)
    }

    /**
     * 添加或更新Bilibili配置。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 添加或更新操作的响应。
     */
    async addOrUpdateBiliConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.post("/api/add_or_update_bili_config", params)
    }

    /**
     * 获取BiliCredential列表。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 获取操作的响应。
     */
    async getBiliCredntialList(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_bili_credential_list", params)
    }

    /**
     * 刷新BiliCredential。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 刷新操作的响应。
     */
    async refreshBiliCredential(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/refresh_bili_credential", params)
    }

    /**
     * 根据主键删除BiliCredential。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 删除操作的响应。
     */
    async deleteBiliCredential(params: {}): Promise<AxiosResponse<any>>{
        return await client.post("/api/delete_bili_credential", params)
    }

    /**
     * 获取BiliCredential的二维码。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 获取操作的响应。
     */
    async getBiliCredentialCode(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_bili_credential_code", params)
    }

    /**
     * 检查二维码状态。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 检查操作的响应。
     */
    async checkQrCode(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/check_qr_code", params)
    }

    /**
     * 获取抖音配置。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 获取操作的响应。
     */
    async getDyConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_dy_config", params)
    }

    /**
     * 添加或更新抖音配置。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 添加或更新操作的响应。
     */
    async addOrUpdateDyConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.post("/api/add_or_update_dy_config", params)
    }

    /**
     * 根据关键字参数获取全局配置。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 获取操作的响应。
     */
    async getGlobalConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_global_config", params)
    }

    /**
     * 添加或更新全局配置。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 添加或更新操作的响应。
     */
    async addOrUpdateGlobalConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.post("/api/add_or_update_global_config", params)
    }
    
    /**
     * 更新BiliCredential。
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<AxiosResponse<any>>} 更新操作的响应。
     */
    async UpdateBiliCredential(params: {}): Promise<AxiosResponse<any>>{
        return await client.post("/api/update_bili_credential", params)
    }
}

export const request = new Request()