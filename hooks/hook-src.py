import os
import platform
import shutil
import tempfile
import atexit

# PyInstaller hook 变量
datas = []
binaries = []
hiddenimports = []


# --- Logic for packaging Notificator.app on macOS ---
if platform.system() == 'Darwin':
    print("macOS detected. Packaging Notificator.app...")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    notificator_app_src_path = os.path.join(root_dir, 'assets', 'Notificator.app')

    if os.path.isdir(notificator_app_src_path):
        # Create the archive in a temporary directory
        temp_dir_notif = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, temp_dir_notif)

        archive_base_name = os.path.join(temp_dir_notif, 'Notificator.app')
        archive_path = shutil.make_archive(archive_base_name, 'gztar', root_dir=os.path.join(root_dir, 'assets'), base_dir='Notificator.app')

        # Add the created archive to datas
        datas.append((archive_path, '.'))
        print(f"Archived {notificator_app_src_path} to {archive_path} and added to datas.")
    else:
        print(f"Warning: Notificator.app not found at {notificator_app_src_path}. Skipping packaging.")
