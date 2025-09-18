import os
import time
import tomllib
from pathlib import Path


def get_path(*other, dir_name: str):
    """获取数据文件路径"""
    os.makedirs(os.path.expanduser("~/.vsingerboard"), exist_ok=True)
    # dir_path = Path.cwd().joinpath(dir_name)
    dir_path = os.path.expanduser(f"~/.vsingerboard/{dir_name}")
    os.makedirs(dir_path, exist_ok=True)
    cfg_path = os.path.join(dir_path, *other)
    return cfg_path


def get_timespan(time_str):
    """字符串转时间戳"""
    time_array = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    res = int(time.mktime(time_array))
    return res


def timespan_to_localtime(timespan):
    """
    时间戳转字符串
    """
    time_array = time.localtime(timespan)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time


def get_time_difference(live_time: int, now: int):
    """计算开播时间到当前时间的时间差"""
    sub = now - live_time
    m, s = divmod(sub, 60)
    h, m = divmod(m, 60)
    dt = ("%02d:%02d:%02d" % (h, m, s))
    return dt


def get_now():
    now = int(time.time())
    now_str = timespan_to_localtime(now)
    return now_str


def get_pyproject_info():
    file_path = Path.cwd().joinpath("pyproject.toml")
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
        return data
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 未找到。")
        return None
    except Exception as e:
        print(f"解析文件时发生错误: {e}")
        return None


def get_version():
    toml = get_pyproject_info()
    if "project" in toml and "version" in toml["project"]:
        return toml["project"]["version"]
    return "0.0.1"
