# VSingerBoard.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
import platform
import shutil
import tempfile
import configparser
import re
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
# Get version from pyproject.toml
# ver is already defined from get_version()

# Parse the version string
version_parts = ver.split('.')
major = version_parts[0] if len(version_parts) > 0 else '0'
minor = version_parts[1] if len(version_parts) > 1 else '0'
patch = version_parts[2] if len(version_parts) > 2 else '0'

try:
    if os.path.exists(version_path):
        with open(version_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update filevers and prodvers
        new_tuple_str = f"({major}, {minor}, {patch}, 0)"
        content = re.sub(
            r"(filevers|prodvers)=\(\d+,\s*\d+,\s*\d+,\s*\d+\)",
            r"\g<1>=" + new_tuple_str,
            content
        )

        # Update FileVersion and ProductVersion StringStructs
        content = re.sub(
            r"(StringStruct\(u'(?:File|Product)Version',\s*u')(\d+\.\d+\.\d+)(')",
            r"\g<1>" + ver + r"\g<3>",
            content
        )

        with open(version_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated version.txt with version {ver}.")
    else:
        print(f"Warning: {version_path} not found. Skipping version update.")

    # Update the _version.py file to ensure it's in sync
    with open('src/utils/_version.py', 'w', encoding='utf-8') as f:
        f.write(f'__version__ = "{ver}"\n')

except Exception as e:
    print(f"Error updating version.txt or _version.py: {e}")

# --- Collect all submodules and data from specific packages ---
# This is the most robust way to ensure a package is fully included.
bilibili_api_datas, bilibili_api_binaries, bilibili_api_hiddenimports = collect_all('bilibili_api')
tortoise_datas, tortoise_binaries, tortoise_hiddenimports = collect_all('tortoise')
fastapi_datas, fastapi_binaries, fastapi_hiddenimports = collect_all('fastapi')
betterproto2_datas, betterproto2_binaries, betterproto2_hiddenimports = collect_all('betterproto2')
pydantic_datas, pydantic_binaries, pydantic_hiddenimports = collect_all('pydantic')


# --- Define data files ---
# Add the entire wwwroot directory as a single data entry.
datas = [('wwwroot', 'wwwroot'), ('resources/douyinjs', 'resources/douyinjs'), ('resources/icons', 'resources/icons')]
datas += bilibili_api_datas
datas += tortoise_datas
datas += fastapi_datas
datas += betterproto2_datas
datas += pydantic_datas

# --- Define hidden imports ---
# This list contains modules that PyInstaller's static analysis might miss.
hidden_packages = [
    "webview", "uvloop", "uvicorn", "objc", "anyio",
    "aiohttp", "curl_cffi", "jinja2",
    "pyperclip", "requests", "pkg_resources"
]
hidden_packages += bilibili_api_hiddenimports
hidden_packages += tortoise_hiddenimports
hidden_packages += fastapi_hiddenimports
hidden_packages += betterproto2_hiddenimports
hidden_packages += pydantic_hiddenimports

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
all_binaries = bilibili_api_binaries + tortoise_binaries + fastapi_binaries + betterproto2_binaries + pydantic_binaries
a = Analysis(
    ['main.py'],
    pathex=[SPECPATH],
    binaries=all_binaries,
    datas=datas,
    hiddenimports=hidden_packages,
    hookspath=[os.path.join(SPECPATH, 'hooks')],  # 使用绝对路径
    hooksconfig={},
    runtime_hooks=[os.path.join(SPECPATH, 'hooks', 'rthook.py')],
    excludes=[],
    noarchive=False,  # 禁用打包以保持文件名不变
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
    strip=False, # Changed from True to False
    upx=True,
    console=False,  # This is a GUI app, so no console window.
    uac_admin=True,
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
    strip=False, # Changed from True to False
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