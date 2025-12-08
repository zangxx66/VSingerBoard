import os
import hashlib
import random
import string
import urllib.parse
from quickjs import Function
from functools import cache
from src.utils import resource_path, logger


def get_real_path(filename):
    res_path = resource_path("douyinjs")
    js_path = os.path.join(res_path, filename)
    return js_path


@cache
def open_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        ctx = f.read()
        return ctx


def execute_js(*args, js_file: str, func_name: str):
    """
    执行 JavaScript 文件
    :param js_file: JavaScript 文件路径
    :return: 执行结果
    """
    js_path = get_real_path(js_file)
    js_code = open_file(js_path)

    ctx = Function(func_name, js_code)
    return ctx(*args)


def generateSignature(wss, script_file='sign_v1.js'):
    """
    为解决Windows下的编码问题，我们使用上下文管理器在执行JS时临时修补subprocess.Popen的编码。
    """
    params = ("live_id,aid,version_code,webcast_sdk_version,"
              "room_id,sub_room_id,sub_channel_id,did_rule,"
              "user_unique_id,device_platform,device_type,ac,"
              "identity").split(',')
    wss_params = urllib.parse.urlparse(wss).query.split('&')
    wss_maps = {i.split('=')[0]: i.split("=")[-1] for i in wss_params}
    tpl_params = [f"{i}={wss_maps.get(i, '')}" for i in params]
    param = ','.join(tpl_params)
    md5 = hashlib.md5()
    md5.update(param.encode())
    md5_param = md5.hexdigest()

    try:
        signature = execute_js(md5_param, js_file=script_file, func_name="get_sign")
        return signature
    except Exception as e:
        logger.error(e)


def generateMsToken(length=182):
    """
    产生请求头部cookie中的msToken字段，其实为随机的182位字符
    :param length:字符位数
    :return:msToken
    """
    random_str = ''
    base_str = string.ascii_letters + string.digits + '-_'
    _len = len(base_str) - 1
    for _ in range(length):
        random_str += base_str[random.randint(0, _len)]
    return random_str
