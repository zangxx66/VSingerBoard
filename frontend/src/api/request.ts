import { client } from "./client"

class Request {
    /**
     * get_bili_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getBiliConfig(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_bili_config", params)
    }

    /**
     * add_or_update_bili_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdateBiliConfig(params: {}): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_bili_config", params)
    }

    /**
     * get_bili_credential_list.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getBiliCredentialList(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_bili_credential_list", params)
    }

    /**
     * refresh_bili_credential.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async refreshBiliCredential(params: {}): Promise<ResponseModel> {
        return await client.get("/api/refresh_bili_credential", params)
    }

    /**
     * delete_bili_credential.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async deleteBiliCredential(params: {}): Promise<ResponseModel> {
        return await client.post("/api/delete_bili_credential", params)
    }

    /**
     * update_bili_credential.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async updateBiliCredential(params: {}): Promise<ResponseModel> {
        return await client.post("/api/update_bili_credential", params)
    }

    /**
     * get_bili_credential_code.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getBiliCredentialCode(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_bili_credential_code", params)
    }

    /**
     * check_qr_code.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async checkQrCode(params: {}): Promise<ResponseModel> {
        return await client.get("/api/check_qr_code", params)
    }

    /**
     * get_dy_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getDyConfig(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_dy_config", params)
    }

    /**
     * add_or_update_dy_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdateDyConfig(params: {}): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_dy_config", params)
    }

    /**
     * get_global_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getGlobalConfig(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_global_config", params)
    }

    /**
     * add_or_update_global_config.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdateGlobalConfig(params: {}): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_global_config", params)
    }

    /**
     * get_history_list.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getHistoryList(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_history_list", params)
    }

    /**
     * check_update.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async checkUpdate(params: {}): Promise<ResponseModel> {
        return await client.get("/api/check_updates", params)
    }

    /**
     * get_playlist_list.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getPlaylistList(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_playlist_list", params)
    }

    /**
     * get_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async getPlaylist(params: {}): Promise<ResponseModel> {
        return await client.get("/api/get_playlist", params)
    }

    /**
     * add_or_update_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async addOrUpdatePlaylist(params: {}): Promise<ResponseModel> {
        return await client.post("/api/add_or_update_playlist", params)
    }

    /**
     * delete_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async deletePlaylist(params: {}): Promise<ResponseModel> {
        return await client.post("/api/delete_playlist", params)
    }

    /**
     * import_playlist.
     * @param {Object} params 传递给服务器的参数对象。
     * @returns {Promise<ResponseModel>} 操作的响应。
     */
    async importPlaylist(params: {}): Promise<ResponseModel> {
        return await client.post("/api/import_playlist", params)
    }

}

export const request = new Request()
