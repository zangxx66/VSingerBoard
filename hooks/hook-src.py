import os
import platform
import shutil
import tempfile
import atexit


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


# --- Logic for packaging Notificator.app on macOS ---
if platform.system() == 'Darwin':
    print("macOS detected. Packaging Notificator.app...")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    notificator_app_src_path = os.path.join(root_dir, 'resources', 'Notificator.app')

    if os.path.isdir(notificator_app_src_path):
        # Create the archive in a temporary directory
        temp_dir_notif = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, temp_dir_notif)

        archive_base_name = os.path.join(temp_dir_notif, 'Notificator.app')
        archive_path = shutil.make_archive(archive_base_name, 'gztar', root_dir=os.path.join(root_dir, 'resources'), base_dir='Notificator.app')

        # Add the created archive to datas
        datas.append((archive_path, '.'))
        print(f"Archived {notificator_app_src_path} to {archive_path} and added to datas.")
    else:
        print(f"Warning: Notificator.app not found at {notificator_app_src_path}. Skipping packaging.")
