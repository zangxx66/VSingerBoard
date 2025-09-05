import { client } from "./client"

class Request {
    async getSubscribeList(params: {}){
        return await client.get("/api/get_subscribe", params)
    }

    async addSubscribe(params: {}){
        return await client.post("/api/add_subscribe", params)
    }

    async updateSubscribe(params: {}){
        return await client.post("/api/update_subscribe", params)
    }

    async getBiliConfig(params: {}){
        return await client.get("/api/get_bili_config", params)
    }

    async addBiliConfig(params: {}){
        return await client.post("/api/add_bili_config", params)
    }

    async updateBiliConfig(params: {}){
        return await client.post("/api/update_bili_config", params)
    }

    async getBiliCredntialList(params: {}){
        return await client.get("/api/get_bili_credential_list", params)
    }

    async refreshBiliCredential(params: {}){
        return await client.get("/api/refresh_bili_credential", params)
    }

    async getBiliCredentialCode(params: {}){
        return await client.get("/api/get_bili_credential_code", params)
    }

    async checkQrCode(params: {}){
        return await client.get("/api/check_qr_code", params)
    }
}

export const request = new Request()