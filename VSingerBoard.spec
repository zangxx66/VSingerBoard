# VSingerBoard.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import platform
import shutil
import tempfile
import configparser
from PyInstaller.utils.hooks import collect_all

# Use SPECPATH, the PyInstaller global variable for the spec file's directory,
# to ensure imports from local scripts work correctly.
sys.path.insert(0, SPECPATH)

# Print debug information
print(f"Hook path: {os.path.join(SPECPATH, 'hooks')}")
print(f"Hook files available: {os.listdir(os.path.join(SPECPATH, 'hooks'))}")

# Import necessary variables from other project files
from src.utils.tool import get_version

ver = get_version()

# Update version.txt from pyproject.toml before build
version_path = 'version.txt'
version_info = configparser.ConfigParser(interpolation=None)
version_info.optionxform = str  # Preserve case

if os.path.exists(version_path):
    with open(version_path, 'r') as f:
        content = '[version]\n' + f.read()
        version_info.read_string(content)
else:
    version_info.add_section('version')

current_version = version_info.get('version', 'FileVersion', fallback=None)

if current_version != ver:
    print(f"Version changed from {current_version} to {ver}. Updating version.txt.")
    version_info.set('version', 'FileVersion', ver)
    version_info.set('version', 'ProductVersion', ver)
    
    with open(version_path, 'w') as f:
        for key, value in version_info['version'].items():
            f.write(f"{key}={value}\n")
    # Update the _version.py file to ensure it's in sync
    with open('src/utils/_version.py', 'w') as f:
        f.write(f'__version__ = "{ver}"\n')
else:
    print("Version has not changed. No update needed.")

# --- Collect all submodules and data from specific packages ---
# This is the most robust way to ensure a package is fully included.
bilibili_api_datas, bilibili_api_binaries, bilibili_api_hiddenimports = collect_all('bilibili_api')
tortoise_datas, tortoise_binaries, tortoise_hiddenimports = collect_all('tortoise')
execjs_datas, execjs_binaries, execjs_hiddenimports = collect_all('execjs')
notifypy_datas, notifypy_binaries, notifypy_hiddenimports = collect_all('notifypy')


# --- Define data files ---
# Add the entire wwwroot directory as a single data entry.
datas = [('wwwroot', 'wwwroot'), ('resources/douyinjs', 'resources/douyinjs'), ('resources/icons', 'resources/icons')]
datas += bilibili_api_datas
datas += tortoise_datas
datas += execjs_datas
datas += notifypy_datas

# --- Define hidden imports ---
# This list contains modules that PyInstaller's static analysis might miss.
hidden_packages = [
    "webview", "uvloop", "uvicorn", "pydantic", "objc", "anyio", "appdirs",
    "aiohttp", "betterproto", "curl_cffi", "fastapi", "jinja2",
    "pyperclip", "requests", "pkg_resources", "websocket"
]
hidden_packages += bilibili_api_hiddenimports
hidden_packages += tortoise_hiddenimports
hidden_packages += execjs_hiddenimports
hidden_packages += notifypy_hiddenimports

# --- Define the Info.plist dictionary (from py2app options) ---
info_plist = {
    "CFBundleName": "VSingerBoard",
    "CFBundleDisplayName": "点歌姬",
    "CFBundleShortVersionString": ver,
    "CFBundleVersion": ver,
    "CFBundleIdentifier": "com.ricardo.vsingerboard",
    "NSHumanReadableCopyright": "Copyright © 2025 Ricardo All rights reserved.",
    "NSAppTransportSecurity": {
        "NSAllowsArbitraryLoads": True,
        "NSAllowsLocalNetworking": True,
        "NSExceptionDomains": {
            "127.0.0.1": {
                "NSIncludesSubdomains": False,
                "NSTemporaryExceptionAllowsInsecureHTTPLoads": True,
                "NSTemporaryExceptionAllowsInsecureHTTPSLoads": False,
                "NSTemporaryExceptionMinimumTLSVersion": "1.0",
                "NSTemporaryExceptionRequiresForwardSecrecy": False
            }
        }
    },
    "NSMainNibFile": "MainMenu",
    "NSSupportsAutomaticGraphicsSwitching": True,
    "NSBluetoothAlwaysUsageDescription": "This app needs access to Bluetooth",
    "NSBluetoothPeripheralUsageDescription": "This app needs access to Bluetooth",
    "NSCameraUsageDescription": "This app needs access to Camera",
    "NSHighResolutionCapable": True,
    "NSDocumentsFolderUsageDescription": "This app needs access to Documents",
    "NSDownloadsFolderUsageDescription": "This app needs access to Downloads",
    "NSLibraryFolderUsageDescription": "This app needs access to Library"
}

# --- PyInstaller Analysis ---
a = Analysis(
    ['main.py'],
    pathex=[SPECPATH],
    binaries=bilibili_api_binaries + tortoise_binaries + execjs_binaries + notifypy_binaries,
    datas=datas,
    hiddenimports=hidden_packages,
    hookspath=[os.path.join(SPECPATH, 'hooks')],  # 使用绝对路径
    hooksconfig={},
    runtime_hooks=[os.path.join(SPECPATH, 'hooks', 'rthook.py')],
    excludes=[],
    noarchive=True,  # 禁用打包以保持文件名不变
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VSingerBoard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=False,  # This is a GUI app, so no console window.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/logo.ico',
    version='version.txt'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='VSingerBoard',
)

# --- macOS .app Bundle ---
app = BUNDLE(
    coll,
    name='VSingerBoard.app',
    icon='resources/icons/logo.icns',
    bundle_identifier=info_plist['CFBundleIdentifier'],
    info_plist=info_plist,
)