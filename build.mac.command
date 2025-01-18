#!/bin/bash

# 获取脚本所在目录
cd "$(dirname "$0")"

# 设置错误处理
set -e

# 输出带颜色的文本函数
print_color() {
    case $1 in
        "red") printf "\033[0;31m$2\033[0m\n";;
        "green") printf "\033[0;32m$2\033[0m\n";;
        "yellow") printf "\033[0;33m$2\033[0m\n";;
    esac
}

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    print_color "red" "Error: Python 3 is not installed"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    print_color "red" "Error: pip3 is not installed"
    exit 1
fi

# 检查依赖
print_color "yellow" "Checking dependencies..."
pip3 install -r requirements.txt || {
    print_color "red" "Error: Failed to install dependencies"
    exit 1
}

# 检查PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    print_color "yellow" "Installing PyInstaller..."
    pip3 install pyinstaller || {
        print_color "red" "Error: Failed to install PyInstaller"
        exit 1
    }
fi

# 清理旧的构建文件
print_color "yellow" "Cleaning old build files..."
rm -rf dist build

# 执行构建
print_color "yellow" "Building Cursor-auto..."
python3 build.py || {
    print_color "red" "Error: Build failed"
    exit 1
}

print_color "green" "Build completed successfully!"
echo "Press any key to continue..."
read -n 1 