#!/bin/bash

# Exit on any error
set -e

echo "Starting build process for VSingerBoard..."

# --- Frontend Build ---
echo "[1/2] Building frontend assets..."
rm -rf wwwroot

if npm run -C frontend/ build; then
    echo "Frontend build successful."
else
    echo "Error: Frontend build failed."
    exit 1
fi

# --- Application Packaging ---
echo "[2/2] Packaging application..."

# The command is the same for major OSes, but we detect the OS
# to make it easier to add specific logic in the future.
OS="$(uname -s)"
case "${OS}" in
    Linux*)
        echo "Running on Linux."
        ;;
    Darwin*)
        echo "Running on macOS."
        ;;
    CYGWIN*|MINGW*|MSYS*)
        echo "Running on Windows."
        ;;
    *)
        echo "Unsupported operating system: ${OS}"
        exit 1
        ;;
esac

echo "Removed old build and dist directories."
rm -rf build dist


if uv run pyinstaller VSingerBoard.spec; then
    echo "Application packaging successful."
else
    echo "Error: Application packaging failed."
    exit 1
fi

echo "Build finished successfully!"
echo "You can find the distributable application in the 'dist' directory."
