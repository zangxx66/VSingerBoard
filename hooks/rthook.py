import os
import sys
import tarfile
import shutil
import datetime


def get_support_dir():
    """获取当前操作系统的应用支持目录。"""
    if sys.platform == 'darwin':
        return os.path.join(os.path.expanduser('~/Library/Application Support'), 'VSingerBoard')
    elif sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], 'VSingerBoard')
    else:
        return os.path.join(os.path.expanduser('~'), '.config', 'VSingerBoard')


def setup_logging():
    """
    将 stdout 和 stderr 重定向到日志文件。
    这个函数只在打包后的应用中生效。
    """
    if not getattr(sys, 'frozen', False):
        return

    try:
        support_dir = get_support_dir()
        log_dir = os.path.join(support_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        current_date = datetime.date.today().isoformat()
        log_file_path = os.path.join(log_dir, f'runtime-hook-{current_date}.log')

        # 使用 'a' 追加模式，保留多次运行的日志
        log_file = open(log_file_path, 'a', encoding='utf-8')

        sys.stdout = log_file
        sys.stderr = log_file

        print(f"--- 日志开始于 {datetime.datetime.now()} ---")
    except Exception as e:
        # 如果日志设置失败, 打印到原始 stderr
        original_stderr = sys.__stderr__
        print(f"设置日志失败: {e}", file=original_stderr)


def setup_node_runtime():
    """在运行时将 Node.js 归档解压到应用支持目录，并设置环境变量。"""
    if not getattr(sys, 'frozen', False):
        return

    app_support_dir = get_support_dir()
    final_node_dir = os.path.join(app_support_dir, 'node')

    if not os.path.exists(final_node_dir):
        print(f"在 {app_support_dir} 中未找到 Node.js。开始首次解压。")
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(sys.executable))

        node_archive = os.path.join(base_path, 'node.tar.gz')

        if not os.path.exists(node_archive):
            print(f"致命错误: 在 {node_archive} 未找到 node.tar.gz")
            return

        print(f"正在解压 node.tar.gz 到 '{app_support_dir}'")
        try:
            os.makedirs(app_support_dir, exist_ok=True)
            with tarfile.open(node_archive, 'r:gz') as tar:
                tar.extractall(path=app_support_dir)
            print("Node.js 解压到应用支持目录完成。")
        except Exception as e:
            print(f"致命错误: Node.js 解压过程中出错: {e}")
            if os.path.exists(final_node_dir):
                shutil.rmtree(final_node_dir)
            return
    else:
        print("在应用支持目录中已找到 Node.js。跳过解压。")

    if os.path.exists(final_node_dir):
        # 根据操作系统确定 Node.js 的可执行文件路径
        if sys.platform == 'win32':
            # Windows 的 Node.js 发行版通常将可执行文件放在根目录
            node_bin_path = final_node_dir
        else:
            # macOS 和 Linux 则在 'bin' 目录下
            node_bin_path = os.path.join(final_node_dir, 'bin')

        if os.path.isdir(node_bin_path):
            print(f"找到 Node.js 执行文件目录: {node_bin_path}")

            # 将 Node.js 路径添加到 PATH 环境变量
            os.environ['PATH'] = node_bin_path + os.pathsep + os.environ.get('PATH', '')
            print(f"PATH 已更新为: {os.environ['PATH']}")

            # 设置 PyExecJS 使用 Node.js 运行时
            os.environ["EXECJS_RUNTIME"] = "Node"
            print(f"EXECJS_RUNTIME 已设置为: {os.environ['EXECJS_RUNTIME']}")
        else:
            print(f"警告: 在 {final_node_dir} 中未找到预期的 Node.js 执行文件目录。")
    else:
        print("错误: 解压后未找到 Node.js 目录。")


def setup_notificator():
    """
    在 macOS 上，首次运行时将 Notificator.app 包解压到应用支持目录。
    """
    if sys.platform != 'darwin' or not getattr(sys, 'frozen', False):
        return

    app_support_dir = get_support_dir()
    final_notificator_path = os.path.join(app_support_dir, 'Notificator.app')

    if not os.path.exists(final_notificator_path):
        print(f"在 {app_support_dir} 中未找到 Notificator.app。开始首次解压。")
        try:
            base_path = sys._MEIPASS
            notificator_archive = os.path.join(base_path, 'Notificator.app.tar.gz')

            if not os.path.exists(notificator_archive):
                print(f"致命错误: 在 {notificator_archive} 未找到 Notificator.app.tar.gz")
                return

            print(f"正在解压 Notificator.app.tar.gz 到 '{app_support_dir}'")
            os.makedirs(app_support_dir, exist_ok=True)
            shutil.unpack_archive(notificator_archive, app_support_dir)
            print("Notificator.app 解压到应用支持目录完成。")

        except Exception as e:
            print(f"致命错误: Notificator.app 解压过程中出错: {e}")
            if os.path.exists(final_notificator_path):
                shutil.rmtree(final_notificator_path)  # 清理部分解压
            return
    else:
        print("在应用支持目录中已找到 Notificator.app。跳过解压。")


setup_logging()
setup_node_runtime()
setup_notificator()
