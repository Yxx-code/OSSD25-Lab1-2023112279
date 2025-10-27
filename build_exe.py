#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京剧脸谱虚拟交互体验系统 - 打包脚本
使用PyInstaller将Python程序打包为可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("正在安装 PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ PyInstaller 安装失败")
            return False

def build_tkinter_version():
    """构建tkinter版本"""
    print("\n=== 构建 tkinter 版本 ===")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=PekingOpera_Tkinter",
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "--add-data=requirements.txt;.",
        "peking_opera_desktop.py"
    ]
    
    # 移除空的icon参数
    cmd = [arg for arg in cmd if arg]
    
    try:
        subprocess.check_call(cmd)
        print("✓ tkinter 版本构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ tkinter 版本构建失败: {e}")
        return False

def build_pyqt_version():
    """构建PyQt5版本"""
    print("\n=== 构建 PyQt5 版本 ===")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=PekingOpera_Advanced",
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "--add-data=requirements.txt;.",
        "peking_opera_advanced.py"
    ]
    
    # 移除空的icon参数
    cmd = [arg for arg in cmd if arg]
    
    try:
        subprocess.check_call(cmd)
        print("✓ PyQt5 版本构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyQt5 版本构建失败: {e}")
        return False

def create_installer_script():
    """创建安装脚本"""
    print("\n=== 创建安装脚本 ===")
    
    # Windows安装脚本
    installer_script = """@echo off
echo 京剧脸谱虚拟交互体验系统 - 安装程序
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 检测到Python，开始安装依赖包...
echo.

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖包
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 安装失败，请检查网络连接或Python环境
    pause
    exit /b 1
)

echo.
echo 安装完成！
echo.
echo 使用方法:
echo 1. 运行 tkinter 版本: python peking_opera_desktop.py
echo 2. 运行 PyQt5 版本: python peking_opera_advanced.py
echo 3. 或直接运行可执行文件
echo.
pause
"""
    
    with open("install_desktop.bat", "w", encoding="utf-8") as f:
        f.write(installer_script)
    
    # Linux/macOS安装脚本
    installer_script_sh = """#!/bin/bash

echo "京剧脸谱虚拟交互体验系统 - 安装程序"
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
echo "1. 运行 tkinter 版本: python3 peking_opera_desktop.py"
echo "2. 运行 PyQt5 版本: python3 peking_opera_advanced.py"
echo "3. 或直接运行可执行文件"
echo
"""
    
    with open("install_desktop.sh", "w", encoding="utf-8") as f:
        f.write(installer_script_sh)
    
    # 设置执行权限
    os.chmod("install_desktop.sh", 0o755)
    
    print("✓ 安装脚本创建成功")

def create_readme():
    """创建README文件"""
    readme_content = """# 京剧脸谱虚拟交互体验系统 - 桌面版

基于图片识别的人脸检测和脸谱应用系统，支持实时摄像头和图片文件处理。

## 功能特性

- 🎭 支持四种经典京剧脸谱类型：生角、旦角、净角、丑角
- 📷 支持实时摄像头和图片文件输入
- 🎨 实时人脸检测和关键点定位
- ⚙️ 丰富的参数调节选项
- 💾 支持图片保存和导出
- 🖥️ 现代化的用户界面

## 系统要求

- Python 3.8 或更高版本
- Windows 10/11, macOS 10.14+, 或 Linux
- 摄像头（用于实时体验）

## 安装方法

### 方法1：使用安装脚本（推荐）

**Windows:**
```bash
# 双击运行
install_desktop.bat

# 或命令行运行
install_desktop.bat
```

**Linux/macOS:**
```bash
# 运行安装脚本
./install_desktop.sh
```

### 方法2：手动安装

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
# tkinter版本（基础版）
python peking_opera_desktop.py

# PyQt5版本（高级版）
python peking_opera_advanced.py
```

## 使用方法

### 基础版本（tkinter）

1. 运行 `peking_opera_desktop.py`
2. 点击"选择图片"按钮选择图片文件
3. 或点击"打开摄像头"进行实时体验
4. 选择脸谱类型和调节参数
5. 点击"应用脸谱"查看效果
6. 点击"保存图片"保存结果

### 高级版本（PyQt5）

1. 运行 `peking_opera_advanced.py`
2. 在"图片"选项卡中选择图片或打开摄像头
3. 在"脸谱"选项卡中选择脸谱类型
4. 在"参数"选项卡中调节效果参数
5. 在"高级"选项卡中设置检测和渲染选项
6. 实时查看效果并保存图片

## 脸谱类型说明

- **生角**：正直英俊的男性角色，妆容简洁大方
- **旦角**：女性角色，妆容精致优雅，色彩柔和
- **净角**：性格鲜明的男性角色，色彩浓烈，图案复杂
- **丑角**：喜剧角色，白鼻梁特征鲜明，表情夸张

## 技术特性

- **人脸检测**：基于MediaPipe的468个关键点检测
- **实时渲染**：OpenCV图像处理和实时效果应用
- **用户界面**：tkinter和PyQt5双版本支持
- **跨平台**：支持Windows、macOS和Linux

## 文件说明

- `peking_opera_desktop.py` - tkinter版本主程序
- `peking_opera_advanced.py` - PyQt5版本主程序
- `requirements.txt` - Python依赖包列表
- `install_desktop.bat` - Windows安装脚本
- `install_desktop.sh` - Linux/macOS安装脚本
- `build_exe.py` - 打包脚本

## 构建可执行文件

运行打包脚本生成独立的可执行文件：

```bash
python build_exe.py
```

生成的文件位于 `dist/` 目录中。

## 故障排除

### 常见问题

1. **摄像头无法打开**
   - 检查摄像头是否被其他程序占用
   - 确认摄像头权限设置

2. **人脸检测失败**
   - 确保图片中包含清晰的人脸
   - 调整光照条件
   - 尝试不同的图片角度

3. **依赖包安装失败**
   - 更新pip：`python -m pip install --upgrade pip`
   - 使用国内镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

4. **PyQt5安装问题**
   - Windows：可能需要安装Visual C++ Redistributable
   - Linux：可能需要安装系统依赖：`sudo apt install python3-pyqt5`

## 开发说明

本项目基于学术论文《Watching Opera at Your Own Ease: A Virtual Character Experience System for Intelligent Opera Facial Makeup》的技术实现，采用现代计算机视觉和机器学习技术，为用户提供沉浸式的京剧脸谱虚拟体验。

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址：[GitHub链接]
- 邮箱：[联系邮箱]

---

© 2024 京剧脸谱虚拟交互体验系统 | 基于学术研究的技术实现
"""
    
    with open("README_desktop.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✓ README文件创建成功")

def main():
    """主函数"""
    print("京剧脸谱虚拟交互体验系统 - 构建工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return
    
    # 创建安装脚本
    create_installer_script()
    
    # 创建README
    create_readme()
    
    # 询问是否构建可执行文件
    choice = input("\n是否构建可执行文件？(y/n): ").lower().strip()
    if choice in ['y', 'yes', '是']:
        # 清理之前的构建文件
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        if os.path.exists("build"):
            shutil.rmtree("build")
        
        # 构建两个版本
        success1 = build_tkinter_version()
        success2 = build_pyqt_version()
        
        if success1 or success2:
            print("\n✓ 构建完成！")
            print("可执行文件位于 dist/ 目录中")
            
            # 创建发布目录
            release_dir = Path("release")
            release_dir.mkdir(exist_ok=True)
            
            # 复制文件到发布目录
            if success1:
                shutil.copy2("dist/PekingOpera_Tkinter.exe", "release/")
            if success2:
                shutil.copy2("dist/PekingOpera_Advanced.exe", "release/")
            
            # 复制其他文件
            files_to_copy = [
                "requirements.txt",
                "install_desktop.bat",
                "install_desktop.sh",
                "README_desktop.md"
            ]
            
            for file in files_to_copy:
                if os.path.exists(file):
                    shutil.copy2(file, "release/")
            
            print(f"发布文件已复制到 {release_dir.absolute()} 目录")
        else:
            print("\n✗ 构建失败")
    else:
        print("\n跳过可执行文件构建")
    
    print("\n构建工具运行完成！")

if __name__ == "__main__":
    main()
