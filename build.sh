#!/bin/bash

# 遇到任何错误立即退出
set -e

export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn

echo "Starting flet build procss..."

# 从 pyproject.tmol 获取版本号
VERSION=$(grep -m 1 'version = ' pyproject.toml | cut -d '"' -f 2)
if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from pyproject.toml"
    exit 1
fi
echo "Detected Version: $VERSION"

# 同步到代码中
echo "__version__ = \"$VERSION\"" > src/utils/_version.py

# 从 uv.lock 获取 flet 版本号
FLET_VER=$(awk '/\[\[package\]\]/ {p=0} /name = "flet"/ {p=1} p && /version = / {split($0, a, "\""); print a[2]; exit}' uv.lock)

# 获取系统参数
OS="$(uname -s)"
ARCH="$(arch)"
BUILD_NUM="$(date +%Y%m%d%H%M%S)"
case "${OS}" in
    Darwin*)
        PLATFORM="macos"
        echo "Running on macOS."
        ;;
    CYGWIN*|MINGW*|MSYS*)
        PLATFORM="windows"
        echo "Running on Windows."
        ;;
    *)
        PLATFORM="linux"
        echo "Running on Linux."
        ;;
esac

# 移除上一次的build产物
echo "Removing old build and dist..."
rm -rf build dist

# 拼接参数
ARGS=(
    "$PLATFORM"
    "--arch" "$ARCH"
    "--artifact" "VSingerBoard"
    "--build-number" "$BUILD_NUM"
    "--build-version" "$VERSION"
    "--bundle-id" "com.ricardo.vsingerboard"
    "--cleanup-app"
    "--cleanup-packages"
    "--clear-cache"
    "--company" "想象力有限公司"
    "--compile-app"
    "--compile-packages"
    "--copyright" "Copyright © 2026 Ricardo All rights reserved."
    "--description" "VSingerBoard - 多平台点歌姬"
    "--exclude" ".github"
    "--exclude" ".git"
    "--exclude" ".venv"
    "--exclude" ".vscode"
    "--exclude" "build"
    "--exclude" "dist"
    "--exclude" "doc"
    "--exclude" "hooks"
    "--exclude" "tests"
    "--exclude" ".gitignore"
    "--exclude" "build.sh"
    "--exclude" "pack.sh"
    "--exclude" "README.md"
    "--exclude" "uv.lock"
    "--exclude" "version.txt"
    "--exclude" "VSingerBoard.spec"
    "--exclude" "pyproject.toml"
    "--exclude" ".python-version"
    "--org" "com.ricardo"
    "--permissions" "photo_library"
    "--product" "VSingerBoard"
    "--skip-flutter-doctor"
    "--template-ref" "$FLET_VER"
    "--verbose"
)

echo "Running flet build with arguments..."

# 开始打包
if uv run fs-build "${ARGS[@]}"; then
    mkdir dist
    mv build/"$PLATFORM"/** dist/
    echo "Application packaging successful."
else
    echo "Error: Application packaging failed."
    exit 1
fi

echo "Build finished successfully!"
echo "You can find the distributable application in the 'dist' directory."