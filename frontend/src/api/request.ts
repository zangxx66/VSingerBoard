import { client } from "./client"

class Request {
    async getBiliConfig(params: {}){
        return await client.get("/api/get_bili_config", params)
    }

    async addOrUpdateBiliConfig(params: {}){
        return await client.post("/api/add_or_update_bili_config", params)
    }

    async getBiliCredntialList(params: {}){
        return await client.get("/api/get_bili_credential_list", params)
    }

    async refreshBiliCredential(params: {}){
        return await client.get("/api/refresh_bili_credential", params)
    }

    async deleteBiliCredential(params: {}){
        return await client.post("/api/delete_bili_credential", params)
    }

    async getBiliCredentialCode(params: {}){
        return await client.get("/api/get_bili_credential_code", params)
    }

    async checkQrCode(params: {}){
        return await client.get("/api/check_qr_code", params)
    }
}

export const request = new Request()