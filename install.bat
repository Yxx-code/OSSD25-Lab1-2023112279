@echo off
chcp 65001 >nul
title 京剧脸谱系统 v2.0 - 安装程序

echo.
echo ================================
echo   京剧脸谱系统 v2.0 - 安装程序
echo ================================
echo.

REM 检查Python是否安装
echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到Python
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
) else (
    echo ✅ Python环境检测成功
)

echo.
echo [2/3] 升级pip...
python -m pip install --upgrade pip

echo.
echo [3/3] 安装依赖包...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ 安装失败！
    echo 请检查网络连接或Python环境
    pause
    exit /b 1
)

echo.
echo ================================
echo       安装完成！
echo ================================
echo.
echo 使用方法:
echo 1. 运行启动器: python run.py
echo 2. 基础版: python peking_opera_desktop.py
echo 3. 高级版: python peking_opera_advanced.py
echo.
pause
