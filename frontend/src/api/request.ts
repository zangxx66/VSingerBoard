import { client } from "./client"

class Request {
    /**
     * get_bili_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getBiliConfig(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_bili_config", params)
    }

    /**
     * add_or_update_bili_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdateBiliConfig(params: object): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_bili_config", params)
    }

    /**
     * get_bili_credential_list.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getBiliCredentialList(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_bili_credential_list", params)
    }

    /**
     * refresh_bili_credential.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async refreshBiliCredential(params: object): Promise<ResponseModel> {
        return await client.get("/api/refresh_bili_credential", params)
    }

    /**
     * delete_bili_credential.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async deleteBiliCredential(params: object): Promise<ResponseModel> {
        return await client.post("/api/delete_bili_credential", params)
    }

    /**
     * update_bili_credential.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async updateBiliCredential(params: object): Promise<ResponseModel> {
        return await client.post("/api/update_bili_credential", params)
    }

    /**
     * get_bili_credential_code.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getBiliCredentialCode(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_bili_credential_code", params)
    }

    /**
     * check_qr_code.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async checkQrCode(params: object): Promise<ResponseModel> {
        return await client.get("/api/check_qr_code", params)
    }

    /**
     * get_dy_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getDyConfig(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_dy_config", params)
    }

    /**
     * add_or_update_dy_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdateDyConfig(params: object): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_dy_config", params)
    }

    /**
     * get_global_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getGlobalConfig(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_global_config", params)
    }

    /**
     * add_or_update_global_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdateGlobalConfig(params: object): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_global_config", params)
    }

    /**
     * get_history_list.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getHistoryList(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_history_list", params)
    }

    /**
     * check_update.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async checkUpdate(params: object): Promise<ResponseModel> {
        return await client.get("/api/check_updates", params)
    }

    /**
     * get_playlist_list.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getPlaylistList(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_playlist_list", params)
    }

    /**
     * get_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getPlaylist(params: object): Promise<ResponseModel> {
        return await client.get("/api/get_playlist", params)
    }

    /**
     * add_or_update_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdatePlaylist(params: object): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_playlist", params)
    }

    /**
     * delete_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async deletePlaylist(params: object): Promise<ResponseModel> {
        return await client.post("/api/delete_playlist", params)
    }

    /**
     * import_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async importPlaylist(params: object): Promise<ResponseModel> {
        return await client.post("/api/import_playlist", params)
    }

}

export const request = new Request()
