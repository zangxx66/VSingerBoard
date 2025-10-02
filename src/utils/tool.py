import os
import sys
import time
import tomllib
import appdirs
import logging
import getpass
import requests
import re
from pathlib import Path
from ._version import __version__ as CURRENT_VERSION

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


def check_for_updates():
    """
    检查 VSingerBoard 的最新版本信息。

    会返回一个 dict，包含以下字段：

    - code: 0 表示当前已是最新版本，-1 表示检查更新失败，1 表示发现新版本。
    - version: 当前是最新版本，否则为当前版本。
    - url: 新版本的下载 URL。
    - body: 新版本的发布说明。
    - published_at: 新版本的发布时间。
    - msg: 检查结果的提示信息。

    如果检查更新失败，会返回一个包含错误信息的 dict。
    """
    repo_url = "https://api.github.com/repos/zangxx66/VSingerBoard/releases/latest"

    def compare_versions(v1, v2):
        v1_main_str, *v1_pre_list = v1.split('-', 1)
        v2_main_str, *v2_pre_list = v2.split('-', 1)

        v1_main = [int(p) for p in v1_main_str.split('.')]
        v2_main = [int(p) for p in v2_main_str.split('.')]

        max_len = max(len(v1_main), len(v2_main))
        v1_main.extend([0] * (max_len - len(v1_main)))
        v2_main.extend([0] * (max_len - len(v2_main)))

        if v1_main > v2_main:
            return 1
        if v1_main < v2_main:
            return -1

        # 主线版本相同，检查pre-release标签
        v1_pre = v1_pre_list[0] if v1_pre_list else None
        v2_pre = v2_pre_list[0] if v2_pre_list else None

        if v1_pre and not v2_pre:
            return -1
        if not v1_pre and v2_pre:
            return 1

        if v1_pre and v2_pre:
            p1_parts = v1_pre.split('.')
            p2_parts = v2_pre.split('.')

            max_len_pre = max(len(p1_parts), len(p2_parts))

            for i in range(max_len_pre):
                if i >= len(p1_parts):
                    return -1
                if i >= len(p2_parts):
                    return 1

                part1 = p1_parts[i]
                part2 = p2_parts[i]

                is_part1_digit = part1.isdigit()
                is_part2_digit = part2.isdigit()

                if is_part1_digit and is_part2_digit:
                    num1 = int(part1)
                    num2 = int(part2)
                    if num1 > num2:
                        return 1
                    if num1 < num2:
                        return -1
                elif is_part1_digit:
                    return -1
                elif is_part2_digit:
                    return 1
                else:
                    if part1 > part2:
                        return 1
                    if part1 < part2:
                        return -1

            return 0

    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        latest_release = response.json()

        # 区分处理有release和没有release的场景
        if "tag_name" not in latest_release:
            # 场景: 没有release, API返回 "message": "Not Found"
            return {"code": -1, "version": CURRENT_VERSION, "url": "", "body": "", "published_at": "", "msg": "当前没有发布任何版本。"}

        latest_version_tag = latest_release["tag_name"]

        version_pattern = re.compile(r"v?(\d+\.\d+\.\d+(?:-[\w\.]+)*)")

        latest_match = version_pattern.search(latest_version_tag)
        current_match = version_pattern.search(CURRENT_VERSION)

        if not latest_match:
            logger.error(f"Could not parse version from tag: {latest_version_tag}")
            return {"code": -1, "version": CURRENT_VERSION, "url": "", "body": "", "published_at": "", "msg": "检查更新失败: 无法解析最新版本号"}

        latest_version = latest_match.group(1)
        current_version_parsed = current_match.group(1) if current_match else CURRENT_VERSION

        is_current_pre = '-' in current_version_parsed
        is_latest_pre = '-' in latest_version

        is_update = False
        # 如果当前是pre-release，它可以被更新为新的pre-release或稳定版本。
        # 如果当前是稳定版本，它只能被更新为新的稳定版本。
        if is_current_pre or not is_latest_pre:
            if compare_versions(latest_version, current_version_parsed) > 0:
                is_update = True

        if is_update:
            return {"code": 0, "version": latest_version_tag, "url": latest_release["html_url"], "body": latest_release["body"], "published_at": latest_release["published_at"], "msg": f"发现新版本: {latest_version} (当前版本: {current_version_parsed})"}
        else:
            return {"code": 0, "version": latest_version_tag, "url": "", "body": latest_release["body"], "published_at": latest_release["published_at"], "msg": "当前已是最新版本。"}
    except Exception as e:
        logger.exception(f"检查更新失败: {e}")
        return {"code": -1, "version": CURRENT_VERSION, "url": "", "body": "", "published_at": "", "msg": "检查更新失败"}
