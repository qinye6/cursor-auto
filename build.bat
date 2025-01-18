@echo off
setlocal enabledelayedexpansion

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

:: 检查pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed or not in PATH
    exit /b 1
)

:: 检查依赖
echo Checking dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

:: 检查PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Error: PyInstaller is not installed
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        exit /b 1
    )
)

:: 清理旧的构建文件
echo Cleaning old build files...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

:: 执行构建
echo Building Cursor-auto...
python build.py
if errorlevel 1 (
    echo Error: Build failed
    exit /b 1
)

echo Build completed successfully!
pause 