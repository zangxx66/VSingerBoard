# VSingerBoard.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import platform
import shutil
import tempfile
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

# Update the _version.py file to ensure it's in sync
with open('src/utils/_version.py', 'w') as f:
    f.write(f'__version__ = "{ver}"\n')

# 无需手动准备 JRE，这部分工作将由 hook-jre.py 处理

# --- Collect all submodules and data from specific packages ---
# This is the most robust way to ensure a package is fully included.
bilibili_api_datas, bilibili_api_binaries, bilibili_api_hiddenimports = collect_all('bilibili_api')
tortoise_datas, tortoise_binaries, tortoise_hiddenimports = collect_all('tortoise')
execjs_datas, execjs_binaries, execjs_hiddenimports = collect_all('execjs')


# --- Define data files ---
# Add the entire wwwroot directory as a single data entry.
datas = [('wwwroot', 'wwwroot'), ('douyinjs', 'douyinjs'), ('logo.png', '.'), ('logo.ico', '.'), ('logo.icns', '.')]
datas += bilibili_api_datas
datas += tortoise_datas
datas += execjs_datas

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

# --- Define the Info.plist dictionary (from py2app options) ---
info_plist = {
    "CFBundleName": "VSingerBoard",
    "CFBundleDisplayName": "点歌姬",
    "CFBundleShortVersionString": ver,
    "CFBundleVersion": ver,
    "CFBundleIdentifier": "com.ricardo.vsingerboard",
    "LSMinimumSystemVersion": "13.0",
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
    binaries=bilibili_api_binaries + tortoise_binaries + execjs_binaries,
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
    version_info={
                "CompanyName": "想象力有限公司",
                "FileDescription": "多平台点歌板",
                "FileVersion": ver,
                "InternalName": "VSingerBoard",
                "LegalCopyright": "Copyright © 2025 Ricardo All rights reserved.",
                "OriginalFilename": "VSingerBoard.exe",
                "ProductName": "点歌姬",
                "ProductVersion": ver
            },
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
    icon='logo.ico',
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
    icon='logo.icns',
    bundle_identifier=info_plist['CFBundleIdentifier'],
    info_plist=info_plist,
)