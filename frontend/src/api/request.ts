import { client } from "./client"
import type { AxiosResponse } from "axios"

class Request {
    /**
     * Get bilibili configuration.
     * @param {Object} params Parameters object passed to the server.
     * @returns {Promise<AxiosResponse<any>>} The response of the get operation.
     */
    async getBiliConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_bili_config", params)
    }

    /**
     * Add or update bilibili configuration.
     * @param {Object} params Parameters object passed to the server.
     * @returns {Promise<AxiosResponse<any>>} The response of the add or update operation.
     */
    async addOrUpdateBiliConfig(params: {}): Promise<AxiosResponse<any>>{
        return await client.post("/api/add_or_update_bili_config", params)
    }

    /**
     * Get a list of BiliCredentials.
     * @param {Object} params Parameters object passed to the server.
     * @returns {Promise<AxiosResponse<any>>} The response of the get operation.
     */
    async getBiliCredntialList(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_bili_credential_list", params)
    }

    /**
     * Refresh a BiliCredential.
     * @param {Object} params Parameters object passed to the server.
     * @returns {Promise<AxiosResponse<any>>} The response of the refresh operation.
     */
    async refreshBiliCredential(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/refresh_bili_credential", params)
    }

    /**
     * Delete a BiliCredential by its primary key.
     * @param {Object} params Parameters object passed to the server.
     * @returns {Promise<AxiosResponse<any>>} The response of the delete operation.
     */
    async deleteBiliCredential(params: {}): Promise<AxiosResponse<any>>{
        return await client.post("/api/delete_bili_credential", params)
    }

    /**
     * Get a BiliCredential's QR code.
     * @param {Object} params Parameters object passed to the server.
     * @returns {Promise<AxiosResponse<any>>} The response of the get operation.
     */
    async getBiliCredentialCode(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/get_bili_credential_code", params)
    }

    /**
     * Check the status of a QR code.
     * @param {Object} params Parameters object passed to the server.
     * @returns {Promise<AxiosResponse<any>>} The response of the check operation.
     */
    async checkQrCode(params: {}): Promise<AxiosResponse<any>>{
        return await client.get("/api/check_qr_code", params)
    }
}

export const request = new Request()