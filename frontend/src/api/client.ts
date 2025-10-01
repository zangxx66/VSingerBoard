import axios from "axios"

const instance = axios.create({
    baseURL: "http://127.0.0.1:8000",
    timeout: 5000,
})

instance.interceptors.request.use(
    config => {
        config.headers["x-token"] = window.pywebview.token

        return config
    },
    error => {
        return Promise.reject(error)
    }
)

class httpClient {
    async get(url: string, params: {}){
        return await instance.get(url, { params: params })
    }

    async post(url: string, params: {}){
        return await instance.post(url, params )
    }
}

export const client = new httpClient()
