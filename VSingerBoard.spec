# VSingerBoard.spec
# -*- mode: python ; coding: utf-8 -*-

import sys

# Use SPECPATH, the PyInstaller global variable for the spec file's directory,
# to ensure imports from local scripts work correctly.
sys.path.insert(0, SPECPATH)

# Import necessary variables from other project files
from src.utils import get_version

# --- Define data files ---
# Add the entire wwwroot directory as a single data entry.
# This is a robust way to include all static assets.
datas = [('wwwroot', 'wwwroot')]
hidden_packages =  ["webview", "uvloop", "uvicorn", "tortoise", "pydantic", "anyio"]

# --- Define the Info.plist dictionary (from py2app options) ---
info_plist = {
    "CFBundleName": "VSingerBoard",
    "CFBundleDisplayName": "点歌板",
    "CFBundleVersion": get_version(),
    "CFBundleIdentifier": "com.ricardo.vsingerboard",
    "DTSDKBuild": "24G90",
    "DTSDKName": "macOS 15.0",
    "LSMinimumSystemVersion": "15.0",
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
# This block tells PyInstaller what to analyze: your main script, data files,
# hidden imports, etc.
a = Analysis(
    ['main.py'],
    pathex=[SPECPATH],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_packages,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
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
    strip=False,
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
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VSingerBoard',
)

# --- macOS .app Bundle ---
# This block defines the final macOS application bundle.
app = BUNDLE(
    coll,
    name='VSingerBoard.app',
    icon='logo.icns',
    bundle_identifier=info_plist['CFBundleIdentifier'],
    info_plist=info_plist,
)