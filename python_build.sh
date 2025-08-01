#!/bin/bash
# PyInstaller を使って Python プログラムをEXEにビルド

SCRIPT="log_zipper.py"
DIST_DIR="dist"
BUILD_DIR="build"
EXE_NAME="log_zipper"

# 古いビルドファイルを削除
rm -rf "$DIST_DIR" "$BUILD_DIR" "${SCRIPT%.py}.spec"

# PyInstaller 実行
pyinstaller --onefile --distpath . "$SCRIPT"

