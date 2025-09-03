from pathlib import Path
import time


def get_path(*other, dir_name: str):
    """获取数据文件路径"""
    dir_path = Path.cwd().joinpath(dir_name)
    return str(dir_path.joinpath(*other))


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
