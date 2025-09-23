import axios from "axios"

const instance = axios.create({
    baseURL: "http://127.0.0.1:8000",
    timeout: 5000,
})

class httpClient {
    async get(url: string, params: {}){
        // @ts-ignore
        return await instance.get(url, { params: params, headers: { "x-token": window.pywebview.token } })
    }

    async post(url: string, params: {}){
        // @ts-ignore
        return await instance.post(url, params, { headers: { "x-token": window.pywebview.token } })
    }
}

export const client = new httpClient()
