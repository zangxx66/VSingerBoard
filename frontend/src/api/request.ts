import { client } from "./client"

/**
 * get_bili_config.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getBiliConfig = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_bili_config", params)
}

/**
 * add_or_update_bili_config.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const addOrUpdateBiliConfig = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/add_or_update_bili_config", params)
}

/**
 * get_bili_credential_list.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getBiliCredentialList = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_bili_credential_list", params)
}

/**
 * refresh_bili_credential.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const refreshBiliCredential = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/refresh_bili_credential", params)
}

/**
 * delete_bili_credential.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const deleteBiliCredential = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/delete_bili_credential", params)
}

/**
 * update_bili_credential.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const updateBiliCredential = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/update_bili_credential", params)
}

/**
 * get_bili_credential_code.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getBiliCredentialCode = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_bili_credential_code", params)
}

/**
 * check_qr_code.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const checkQrCode = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/check_qr_code", params)
}

/**
 * get_dy_config.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getDyConfig = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_dy_config", params)
}

/**
 * add_or_update_dy_config.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const addOrUpdateDyConfig = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/add_or_update_dy_config", params)
}

/**
 * get_global_config.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getGlobalConfig = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_global_config", params)
}

/**
 * add_or_update_global_config.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const addOrUpdateGlobalConfig = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/add_or_update_global_config", params)
}

/**
 * get_history_list.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getHistoryList = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_history_list", params)
}

/**
 * check_update.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const checkUpdate = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/check_updates", params)
}

/**
 * get_playlist_list.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getPlaylistList = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_playlist_list", params)
}

/**
 * get_playlist.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const getPlaylist = async (params: object): Promise<ResponseModel> => {
  return await client.get("/api/get_playlist", params)
}

/**
 * add_or_update_playlist.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const addOrUpdatePlaylist = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/add_or_update_playlist", params)
}

/**
 * delete_playlist.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const deletePlaylist = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/delete_playlist", params)
}

/**
 * import_playlist.
 * @param {Object} params 传递给服务器的参数对象。
 * @returns {Promise<ResponseModel>} 操作的响应。
 */
export const importPlaylist = async (params: object): Promise<ResponseModel> => {
  return await client.post("/api/import_playlist", params)
}
