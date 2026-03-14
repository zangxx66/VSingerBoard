#!/bin/bash

# 遇到任何错误立即退出
set -e

echo "Starting flet build process for VSingerBoard..."

# 1. 提取版本号 (从 pyproject.toml 获取)
VERSION=$(grep -m 1 'version = ' pyproject.toml | cut -d '"' -f 2)
if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from pyproject.toml"
    exit 1
fi
echo "Detected Version: $VERSION"

# 2. 同步版本号到代码和资源
echo "__version__ = \"$VERSION\"" > src/utils/_version.py

if [ -f "version.txt" ]; then
    IFS='.' read -r -a VERSION_PARTS <<< "$VERSION"
    MAJOR="${VERSION_PARTS[0]:-0}"
    MINOR="${VERSION_PARTS[1]:-0}"
    PATCH="${VERSION_PARTS[2]:-0}"
    PATCH=$(echo "$PATCH" | grep -oE '^[0-9]+' | head -n 1)
    
    SED_I_ARG=""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        SED_I_ARG="''"
    fi

    sed -i $SED_I_ARG "s/filevers=([0-9]*, [0-9]*, [0-9]*, [0-9]*)/filevers=($MAJOR, $MINOR, $PATCH, 0)/g" version.txt || true
    sed -i $SED_I_ARG "s/prodvers=([0-9]*, [0-9]*, [0-9]*, [0-9]*)/prodvers=($MAJOR, $MINOR, $PATCH, 0)/g" version.txt || true
    sed -i $SED_I_ARG "s/StringStruct(u'FileVersion', u'[^']*')/StringStruct(u'FileVersion', u'$VERSION')/g" version.txt || true
    sed -i $SED_I_ARG "s/StringStruct(u'ProductVersion', u'[^']*')/StringStruct(u'ProductVersion', u'$VERSION')/g" version.txt || true
    echo "Updated version.txt to $VERSION"
fi

# 3. 检测操作系统并设置平台特定参数
OS="$(uname -s)"
case "${OS}" in
    Darwin*)
        PLATFORM="macos"
        ICON="assets/icons/logo.icns"
        EXTRA_ARGS=(
            "--bundle-id" "com.ricardo.vsingerboard"
            "--pyinstaller-build-args=--strip"
            )
        echo "Running on macOS."
        ;;
    CYGWIN*|MINGW*|MSYS*)
        PLATFORM="windows"
        ICON="assets/icons/logo.ico"
        EXTRA_ARGS=(
            "--uac-admin"
            "--onedir"
            "--pyinstaller-build-args=--version-file=version.txt"
            )
        echo "Running on Windows."
        ;;
    *)
        PLATFORM="linux"
        ICON="assests/icons/logo.png"
        EXTRA_ARGS=(
            "--pyinstaller-build-args=--strip"
        )
        echo "Running on Linux."
        ;;
esac

echo "Removing old build and dist directories..."
rm -rf build dist

# 4. 完善 BUILD_ARGS
# 使用 --collect-all 替换简单的 --hidden-import，以确保复杂包的完整性
BUILD_ARGS=(
    # 应用信息
    "--name" "VSingerBoard"
    "--product-name" "点歌姬"
    "--product-version" "$VERSION"
    "--file-version" "$VERSION"
    "--file-description" "VSingerBoard - 多平台点歌姬"
    "--copyright" "Copyright © 2026 Ricardo All rights reserved."
    "--icon" "$ICON"
    "--pyinstaller-build-args=--name=VSingerBoard"
    # 隐式导入 (保留一些通用的)
    "--hidden-import" "anyio"
    "--hidden-import" "aiohttp"
    "--hidden-import" "curl_cffi"
    "--hidden-import" "pkg_resources"
    # 使用 PyInstaller 原生参数完整收集复杂包 (对应原 .spec 中的 collect_all)
    "--pyinstaller-build-args=--collect-all=bilibili_api"
    "--pyinstaller-build-args=--collect-all=tortoise"
    "--pyinstaller-build-args=--collect-all=betterproto2"
    "--pyinstaller-build-args=--collect-all=pydantic"
    "--pyinstaller-build-args=--collect-all=aerich"
    "--pyinstaller-build-args=--collect-all=flet"
    "--pyinstaller-build-args=--collect-all=flet-datatable2"
    "--pyinstaller-build-args=--additional-hooks-dir=hooks"
    "--pyinstaller-build-args=--runtime-hook=hooks/rthook.py"
    "--pyinstaller-build-args=--icon=$ICON"
    # 资源文件
    "--pyinstaller-build-args=--add-data=assets/douyinjs:assets/douyinjs"
    "--pyinstaller-build-args=--add-data=assets/icons:assets/icons"
    "--pyinstaller-build-args=--add-data=assets/images:assets/images"
    "--pyinstaller-build-args=--add-data=assets/favicon.png:assets/favicon.png"
    "--pyinstaller-build-args=--add-data=assets/fonts/NotoSansSC-VariableFont_wght.ttf:assets/fonts/NotoSansSC-VariableFont_wght.ttf"

    # 包含平台特定参数
    "${EXTRA_ARGS[@]}"
    "-y"
)

echo "Running flet pack with arguments..."

# 5. 执行打包
if uv run flet pack "${BUILD_ARGS[@]}" main.py; then
    echo "Application packaging successful."
else
    echo "Error: Application packaging failed."
    exit 1
fi

echo "Build finished successfully!"
echo "You can find the distributable application in the 'dist' directory."
