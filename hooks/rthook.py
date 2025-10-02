import os
import sys
import tarfile
import shutil


def get_support_dir():
    """Gets the application support directory for the current OS."""
    if sys.platform == 'darwin':
        return os.path.join(os.path.expanduser('~/Library/Application Support'), 'VSingerBoard')
    elif sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], 'VSingerBoard')
    else:
        return os.path.join(os.path.expanduser('~'), '.config', 'VSingerBoard')


def setup_node_runtime():
    """在运行时将 Node.js 归档解压到应用支持目录，并设置环境变量。"""
    if not getattr(sys, 'frozen', False):
        return

    app_support_dir = get_support_dir()
    final_node_dir = os.path.join(app_support_dir, 'node')

    if not os.path.exists(final_node_dir):
        print(f"Node.js not found in {app_support_dir}. Starting first-time extraction.")
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(sys.executable))

        node_archive = os.path.join(base_path, 'node.tar.gz')  # <-- Changed to .tar.gz

        if not os.path.exists(node_archive):
            print(f"FATAL: node.tar.gz not found at {node_archive}")
            return

        print(f"Extracting node.tar.gz to '{app_support_dir}'")
        try:
            os.makedirs(app_support_dir, exist_ok=True)
            with tarfile.open(node_archive, 'r:gz') as tar:  # <-- Changed to r:gz
                tar.extractall(path=app_support_dir)
            print("Node.js extraction to Application Support complete.")
        except Exception as e:
            print(f"FATAL: Error during Node.js extraction: {e}")
            if os.path.exists(final_node_dir):
                shutil.rmtree(final_node_dir)
            return
    else:
        print("Node.js already found in Application Support. Skipping extraction.")

    if os.path.exists(final_node_dir):
        node_bin_path = os.path.join(final_node_dir, 'bin')
        if os.path.isdir(node_bin_path):
            print(f"Node.js bin path found: {node_bin_path}")

            os.environ['PATH'] = node_bin_path + os.pathsep + os.environ.get('PATH', '')
            print(f"PATH set to: {os.environ['PATH']}")

            os.environ["EXECJS_RUNTIME"] = "Node"
            print(f"EXECJS_RUNTIME set to: {os.environ['EXECJS_RUNTIME']}")
        else:
            print(f"Warning: Could not find bin directory in {final_node_dir}")
    else:
        print("Error: final_node_dir path does not exist after extraction attempt.")


setup_node_runtime()
