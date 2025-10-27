#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京剧脸谱系统 v2.0 - 简化启动器
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """检查依赖包是否安装"""
    required_packages = ['cv2', 'mediapipe', 'PIL', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'mediapipe':
                import mediapipe
            elif package == 'PIL':
                from PIL import Image
            elif package == 'numpy':
                import numpy
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """安装依赖包"""
    try:
        print("正在安装依赖包...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("依赖包安装完成！")
        return True
    except subprocess.CalledProcessError:
        print("依赖包安装失败！")
        return False

def run_basic():
    """运行基础版"""
    try:
        subprocess.run([sys.executable, "peking_opera_desktop.py"])
    except FileNotFoundError:
        messagebox.showerror("错误", "找不到 peking_opera_desktop.py 文件")
    except Exception as e:
        messagebox.showerror("错误", f"运行失败: {str(e)}")

def run_advanced():
    """运行高级版"""
    try:
        # 检查PyQt5是否安装
        try:
            import PyQt5
        except ImportError:
            messagebox.showwarning("警告", "PyQt5未安装，正在安装...")
            if not install_dependencies():
                return
        
        subprocess.run([sys.executable, "peking_opera_advanced.py"])
    except FileNotFoundError:
        messagebox.showerror("错误", "找不到 peking_opera_advanced.py 文件")
    except Exception as e:
        messagebox.showerror("错误", f"运行失败: {str(e)}")

def show_launcher():
    """显示启动器界面"""
    root = tk.Tk()
    root.title("京剧脸谱系统 v2.0")
    root.geometry("400x300")
    root.configure(bg='#2F1B14')
    
    # 标题
    title_label = tk.Label(
        root,
        text="🎭 京剧脸谱系统 v2.0",
        font=('Microsoft YaHei', 16, 'bold'),
        fg='#FFD700',
        bg='#2F1B14'
    )
    title_label.pack(pady=20)
    
    # 副标题
    subtitle_label = tk.Label(
        root,
        text="请选择要运行的版本",
        font=('Microsoft YaHei', 12),
        fg='#FFE4B5',
        bg='#2F1B14'
    )
    subtitle_label.pack(pady=10)
    
    # 按钮框架
    button_frame = tk.Frame(root, bg='#2F1B14')
    button_frame.pack(pady=20)
    
    # 基础版按钮
    basic_btn = tk.Button(
        button_frame,
        text="基础版 (tkinter)",
        command=lambda: [root.destroy(), run_basic()],
        font=('Microsoft YaHei', 12, 'bold'),
        bg='#8B0000',
        fg='white',
        relief='raised',
        bd=3,
        width=15,
        height=2
    )
    basic_btn.pack(pady=10)
    
    # 高级版按钮
    advanced_btn = tk.Button(
        button_frame,
        text="高级版 (PyQt5)",
        command=lambda: [root.destroy(), run_advanced()],
        font=('Microsoft YaHei', 12, 'bold'),
        bg='#8B0000',
        fg='white',
        relief='raised',
        bd=3,
        width=15,
        height=2
    )
    advanced_btn.pack(pady=10)
    
    # 退出按钮
    exit_btn = tk.Button(
        root,
        text="退出",
        command=root.quit,
        font=('Microsoft YaHei', 10),
        bg='#2F4F4F',
        fg='white',
        relief='raised',
        bd=2,
        width=10
    )
    exit_btn.pack(pady=20)
    
    root.mainloop()

def main():
    """主函数"""
    print("京剧脸谱系统 v2.0 - 启动器")
    print("=" * 30)
    
    # 检查依赖包
    missing = check_dependencies()
    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        print("正在安装依赖包...")
        
        if not install_dependencies():
            print("依赖包安装失败，请手动运行: pip install -r requirements.txt")
            return
    
    # 显示启动器界面
    show_launcher()

if __name__ == "__main__":
    main()
