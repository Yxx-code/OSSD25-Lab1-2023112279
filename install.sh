#!/bin/bash

echo "正在安装京剧脸谱虚拟交互体验系统..."
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未检测到Python3，请先安装Python 3.8或更高版本"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

echo "检测到Python3，开始安装依赖包..."
echo

# 升级pip
python3 -m pip install --upgrade pip

# 安装依赖包
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "安装失败，请检查网络连接或Python环境"
    exit 1
fi

echo
echo "安装完成！"
echo
echo "使用方法:"
echo "1. 运行: python3 peking_opera_desktop.py"
echo "2. 或者: chmod +x peking_opera_desktop.py && ./peking_opera_desktop.py"
echo
