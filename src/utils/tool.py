import os
import sys
import time
import tomllib
import appdirs
import logging
import getpass
from pathlib import Path

logger = logging.getLogger("danmaku")


def get_path(*other, dir_name: str):
    """获取数据文件路径"""
    app_data_dir = appdirs.user_data_dir("VSingerBoard")
    dir_path = os.path.join(app_data_dir, dir_name)
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
    """
    获取当前时间的字符串表示

    Returns:
        str: 当前时间的字符串表示，格式为 "YYYY-MM-DD HH:mm:ss"
    """
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
        logger.error(f"错误：文件 '{file_path}' 未找到。")
        return None
    except Exception as e:
        logger.error(f"解析文件时发生错误: {e}")
        return None


def get_version():
    """
    获取当前项目的版本号

    Returns:
        str: 当前项目的版本号，如果无法读取项目配置文件则返回 "0.0.1"
    """
    toml = get_pyproject_info()
    if "project" in toml and "version" in toml["project"]:
        return toml["project"]["version"]
    return "0.0.1"


def resource_path(relative_path):
    """
    获取资源文件的路径

    如果当前环境是 PyInstaller 创建的，那么将使用 _MEIPASS 中的路径作为基路径。
    否则，基路径将是项目的根目录。

    Args:
        relative_path (str): 资源文件相对路径

    Returns:
        str: 资源文件的绝对路径
    """
    try:
        # PyInstaller 创建一个临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 未打包状态下，基路径就是项目根目录
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_autostart_command():
    if getattr(sys, "frozen", False):
        return [f'"{sys.executable}"']
    else:
        return [f'"{sys.executable}"', f'"{os.path.abspath(sys.argv[0])}"']


def setup_autostart(enable: bool):
    """
    设置应用程序的自启动功能

    Args:
        enable (bool): 是否启用自启动

    Returns:
        bool: 是否成功设置自启动
    """
    APP_NAME = "VSingerBoard"
    command = get_autostart_command()
    try:
        if sys.platform == "win32":
            import winreg
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as run_key:
                if enable:
                    cmd = " ".join(command)
                    winreg.SetValueEx(run_key, APP_NAME, 0, winreg.REG_SZ, cmd)
                    logger.info(f"Windows autostart enabled: {command}")
                else:
                    winreg.DeleteValue(run_key, APP_NAME)
                    logger.info("Windows autostart disabled.")
                return True
        elif sys.platform.startswith("linux"):
            user = getpass.getuser()
            autostart_dir = f"/home/{user}/.config/autostart/"
            desktop_entry_path = os.path.join(autostart_dir, f"{APP_NAME.lower()}.desktop")
            if enable:
                cmd = " ".join(command)
                desktop_entry_content = f'''
                [Desktop Entry]
                Type=Application
                Name={APP_NAME}
                Exec={cmd}
                Terminal=false
                Comment=Start {APP_NAME} at login
                '''
                os.makedirs(autostart_dir, exist_ok=True)
                with open(desktop_entry_path, 'w') as f:
                    f.write(desktop_entry_content)
                logger.info(f"Linux autostart enabled: {cmd}")
            else:
                if os.path.exists(desktop_entry_path):
                    os.remove(desktop_entry_path)
                logger.info("Linux autostart disabled.")
            return True
        elif sys.platform == "darwin":
            user = getpass.getuser()
            plist_path = f"/Users/{user}/Library/LaunchAgents/com.{APP_NAME.lower()}.plist"
            if enable:
                program_args_xml = "".join([f"<string>{arg.strip('\"')}</string>" for arg in command])
                plist_content = f'''
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>com.{APP_NAME.lower()}</string>
                    <key>ProgramArguments</key>
                    <array>{program_args_xml}</array>
                    <key>RunAtLoad</key>
                    <true/>
                </dict>
                </plist>
                '''
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                logger.info(f"macOS autostart enabled: {' '.join(command)}")
            else:
                if os.path.exists(plist_path):
                    os.remove(plist_path)
                logger.info("macOS autostart disabled.")
            return True
        else:
            raise Exception(f"Autostart not supported on platform: {sys.platform}")
    except Exception as e:
        logger.error(f"设置自启动失败：{e}")
        return False
