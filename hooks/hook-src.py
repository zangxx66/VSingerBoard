import os
import platform


def get_archive_path():
    """获取当前平台对应的预压缩归档文件路径"""
    arch = platform.machine()
    system = platform.system()

    if system == 'Windows':
        platform_name = 'win-x64'
    elif system == 'Darwin':
        platform_name = 'darwin-arm64' if arch == 'arm64' else 'darwin-x64'
    elif system == 'Linux':
        platform_name = 'linux-x64'
    else:
        return None

    archive_filename = f"{platform_name}.tar.gz"

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    archive_path = os.path.join(root_dir, 'resources', archive_filename)

    if os.path.isfile(archive_path):
        print(f"Found Node.js archive at: {archive_path}")
        return archive_path

    print(f"Warning: Node.js archive not found at {archive_path}")
    return None


# PyInstaller hook 变量
datas = []
binaries = []
hiddenimports = []


archive_path = get_archive_path()
if archive_path:
    # 将预压缩的归档文件添加到 datas 中，目标文件名为 node.tar.gz
    datas.append((archive_path, 'node.tar.gz'))
    print(f"Added {archive_path} to datas as node.tar.gz")
else:
    print("Warning: Node.js archive not found. Skipping Node.js packaging.")
