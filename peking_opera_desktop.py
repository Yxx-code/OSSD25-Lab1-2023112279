#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京剧脸谱虚拟交互体验系统 - 桌面版
基于图片识别的人脸检测和脸谱应用系统
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageTk
import os
import json
from typing import Dict, List, Tuple, Optional
import threading
import time

class PekingOperaDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("京剧脸谱系统 v2.0 - 基础版")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2F1B14')
        
        # 初始化MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 当前图片和脸谱数据
        self.current_image = None
        self.current_landmarks = None
        self.current_makeup_type = "none"
        self.makeup_patterns = self.load_makeup_patterns()
        
        # 界面参数
        self.opacity = 0.8
        self.intensity = 1.0
        self.offset = 0
        self.show_landmarks = True
        self.save_with_landmarks = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = tk.Frame(self.root, bg='#2F1B14')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = tk.Frame(main_frame, bg='#1a0f0a', width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # 右侧图片显示区域
        image_frame = tk.Frame(main_frame, bg='#1a0f0a')
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_control_panel(control_frame)
        self.setup_image_panel(image_frame)
        
    def setup_control_panel(self, parent):
        """设置控制面板"""
        # 标题
        title_label = tk.Label(
            parent, 
            text="🎭 京剧脸谱体验", 
            font=('Microsoft YaHei', 16, 'bold'),
            fg='#FFD700',
            bg='#1a0f0a'
        )
        title_label.pack(pady=20)
        
        # 图片选择区域
        image_section = tk.LabelFrame(
            parent, 
            text="图片选择", 
            font=('Microsoft YaHei', 12, 'bold'),
            fg='#FFD700',
            bg='#1a0f0a',
            bd=2
        )
        image_section.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            image_section,
            text="📁 选择图片",
            command=self.select_image,
            font=('Microsoft YaHei', 10),
            bg='#8B0000',
            fg='white',
            relief=tk.RAISED,
            bd=2
        ).pack(pady=10)
        
        tk.Button(
            image_section,
            text="📷 打开摄像头",
            command=self.open_camera,
            font=('Microsoft YaHei', 10),
            bg='#CD853F',
            fg='white',
            relief=tk.RAISED,
            bd=2
        ).pack(pady=5)
        
        # 脸谱类型选择
        makeup_section = tk.LabelFrame(
            parent,
            text="脸谱类型",
            font=('Microsoft YaHei', 12, 'bold'),
            fg='#FFD700',
            bg='#1a0f0a',
            bd=2
        )
        makeup_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.makeup_var = tk.StringVar(value="none")
        makeup_types = [
            ("无脸谱", "none"),
            ("生角", "sheng"),
            ("旦角", "dan"),
            ("净角", "jing"),
            ("丑角", "chou")
        ]
        
        for text, value in makeup_types:
            tk.Radiobutton(
                makeup_section,
                text=text,
                variable=self.makeup_var,
                value=value,
                command=self.on_makeup_change,
                font=('Microsoft YaHei', 10),
                fg='#FFE4B5',
                bg='#1a0f0a',
                selectcolor='#8B0000',
                activebackground='#1a0f0a',
                activeforeground='#FFD700'
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # 参数调节区域
        params_section = tk.LabelFrame(
            parent,
            text="效果调节",
            font=('Microsoft YaHei', 12, 'bold'),
            fg='#FFD700',
            bg='#1a0f0a',
            bd=2
        )
        params_section.pack(fill=tk.X, padx=10, pady=10)
        
        # 透明度调节
        tk.Label(
            params_section,
            text="透明度:",
            font=('Microsoft YaHei', 10),
            fg='#FFE4B5',
            bg='#1a0f0a'
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        self.opacity_var = tk.DoubleVar(value=80)
        opacity_scale = tk.Scale(
            params_section,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.opacity_var,
            command=self.on_opacity_change,
            bg='#1a0f0a',
            fg='#FFE4B5',
            troughcolor='#8B0000',
            activebackground='#FFD700'
        )
        opacity_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # 颜色强度调节
        tk.Label(
            params_section,
            text="颜色强度:",
            font=('Microsoft YaHei', 10),
            fg='#FFE4B5',
            bg='#1a0f0a'
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        self.intensity_var = tk.DoubleVar(value=100)
        intensity_scale = tk.Scale(
            params_section,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.intensity_var,
            command=self.on_intensity_change,
            bg='#1a0f0a',
            fg='#FFE4B5',
            troughcolor='#8B0000',
            activebackground='#FFD700'
        )
        intensity_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # 位置偏移调节
        tk.Label(
            params_section,
            text="位置偏移:",
            font=('Microsoft YaHei', 10),
            fg='#FFE4B5',
            bg='#1a0f0a'
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        self.offset_var = tk.DoubleVar(value=0)
        offset_scale = tk.Scale(
            params_section,
            from_=-50,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.offset_var,
            command=self.on_offset_change,
            bg='#1a0f0a',
            fg='#FFE4B5',
            troughcolor='#8B0000',
            activebackground='#FFD700'
        )
        offset_scale.pack(fill=tk.X, padx=10, pady=5)
        
        # 高级设置
        advanced_section = tk.LabelFrame(
            parent,
            text="高级设置",
            font=('Microsoft YaHei', 12, 'bold'),
            fg='#FFD700',
            bg='#1a0f0a',
            bd=2
        )
        advanced_section.pack(fill=tk.X, padx=10, pady=10)
        
        self.face_tracking_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_section,
            text="启用面部跟踪",
            variable=self.face_tracking_var,
            font=('Microsoft YaHei', 10),
            fg='#FFE4B5',
            bg='#1a0f0a',
            selectcolor='#8B0000',
            activebackground='#1a0f0a',
            activeforeground='#FFD700'
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self.edge_smoothing_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_section,
            text="边缘平滑处理",
            variable=self.edge_smoothing_var,
            font=('Microsoft YaHei', 10),
            fg='#FFE4B5',
            bg='#1a0f0a',
            selectcolor='#8B0000',
            activebackground='#1a0f0a',
            activeforeground='#FFD700'
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self.show_landmarks_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_section,
            text="显示人脸关键点",
            variable=self.show_landmarks_var,
            command=self.on_show_landmarks_change,
            font=('Microsoft YaHei', 10),
            fg='#FFE4B5',
            bg='#1a0f0a',
            selectcolor='#8B0000',
            activebackground='#1a0f0a',
            activeforeground='#FFD700'
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        self.save_with_landmarks_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            advanced_section,
            text="保存时包含关键点",
            variable=self.save_with_landmarks_var,
            command=self.on_save_with_landmarks_change,
            font=('Microsoft YaHei', 10),
            fg='#FFE4B5',
            bg='#1a0f0a',
            selectcolor='#8B0000',
            activebackground='#1a0f0a',
            activeforeground='#FFD700'
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        # 操作按钮
        button_section = tk.Frame(parent, bg='#1a0f0a')
        button_section.pack(fill=tk.X, padx=10, pady=20)
        
        tk.Button(
            button_section,
            text="🎨 应用脸谱",
            command=self.apply_makeup,
            font=('Microsoft YaHei', 12, 'bold'),
            bg='#8B0000',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            height=2
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            button_section,
            text="💾 保存图片",
            command=self.save_image,
            font=('Microsoft YaHei', 12, 'bold'),
            bg='#CD853F',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            height=2
        ).pack(fill=tk.X, pady=5)
        
        tk.Button(
            button_section,
            text="🔄 重置效果",
            command=self.reset_effects,
            font=('Microsoft YaHei', 12, 'bold'),
            bg='#2F4F4F',
            fg='white',
            relief=tk.RAISED,
            bd=3,
            height=2
        ).pack(fill=tk.X, pady=5)
        
    def setup_image_panel(self, parent):
        """设置图片显示面板"""
        # 图片显示区域
        self.image_label = tk.Label(
            parent,
            text="请选择图片或打开摄像头",
            font=('Microsoft YaHei', 14),
            fg='#FFE4B5',
            bg='#1a0f0a',
            relief=tk.SUNKEN,
            bd=2
        )
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 状态栏
        self.status_label = tk.Label(
            parent,
            text="就绪",
            font=('Microsoft YaHei', 10),
            fg='#00FF00',
            bg='#1a0f0a',
            relief=tk.SUNKEN,
            bd=1
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=(0, 10))
        
    def load_makeup_patterns(self):
        """加载脸谱图案数据"""
        return {
            "sheng": {
                "name": "生角",
                "colors": {"primary": "#F5DEB3", "secondary": "#8B4513", "accent": "#DC143C"},
                "pattern": {
                    "faceOutline": {"color": "#F5DEB3", "opacity": 0.3},
                    "eyebrows": {"style": "straight", "color": "#8B4513", "thickness": 6},
                    "eyeDecoration": {"type": "liner", "color": "#654321", "thickness": 2},
                    "blush": {"color": "#FFB6C1", "opacity": 0.4, "size": 15}
                }
            },
            "dan": {
                "name": "旦角",
                "colors": {"primary": "#FFE4E1", "secondary": "#FFB6C1", "accent": "#FF69B4"},
                "pattern": {
                    "faceOutline": {"color": "#FFE4E1", "opacity": 0.4},
                    "eyebrows": {"style": "curved", "color": "#8B4513", "thickness": 3},
                    "eyeDecoration": {"type": "shadow", "color": "#FFB6C1", "thickness": 8},
                    "blush": {"color": "#FF69B4", "opacity": 0.6, "size": 18}
                }
            },
            "jing": {
                "name": "净角",
                "colors": {"primary": "#4169E1", "secondary": "#000080", "accent": "#FFD700"},
                "pattern": {
                    "faceOutline": {"color": "#4169E1", "opacity": 0.7},
                    "eyebrows": {"style": "upturned", "color": "#000000", "thickness": 10},
                    "eyeDecoration": {"type": "dramatic", "color": "#FFD700", "thickness": 5},
                    "blush": {"color": "#FFD700", "opacity": 0.5, "size": 20}
                }
            },
            "chou": {
                "name": "丑角",
                "colors": {"primary": "#FFFFFF", "secondary": "#FFA500", "accent": "#FF0000"},
                "pattern": {
                    "faceOutline": {"color": "#FFA500", "opacity": 0.5},
                    "eyebrows": {"style": "curved", "color": "#000000", "thickness": 5},
                    "eyeDecoration": {"type": "comic", "color": "#FF0000", "thickness": 4},
                    "blush": {"color": "#FFA500", "opacity": 0.6, "size": 25}
                }
            }
        }
    
    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """加载图片"""
        try:
            # 读取图片
            image = cv2.imread(file_path)
            if image is None:
                messagebox.showerror("错误", "无法读取图片文件")
                return
            
            # 转换颜色空间
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.current_image = image_rgb
            
            # 检测人脸
            self.detect_face()
            
            # 显示图片
            self.display_image(image_rgb)
            
            self.update_status(f"已加载图片: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {str(e)}")
    
    def open_camera(self):
        """打开摄像头"""
        def camera_thread():
            try:
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    messagebox.showerror("错误", "无法打开摄像头，请检查摄像头是否被其他程序占用")
                    return
                
                self.update_status("摄像头已打开，按ESC键退出")
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        print("摄像头读取失败")
                        break
                    
                    # 转换颜色空间
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # 检测人脸
                    try:
                        results = self.face_mesh.process(frame_rgb)
                        if results.multi_face_landmarks:
                            self.current_landmarks = results.multi_face_landmarks[0]
                            # 应用脸谱效果
                            if self.current_makeup_type != "none":
                                frame_rgb = self.apply_makeup_to_image(frame_rgb)
                    except Exception as e:
                        print(f"人脸检测错误: {e}")
                    
                    # 显示图片
                    self.display_image(frame_rgb)
                    
                    # 检查退出条件
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC键
                        break
                
                cap.release()
                cv2.destroyAllWindows()
                self.update_status("摄像头已关闭")
                
            except Exception as e:
                messagebox.showerror("错误", f"摄像头运行失败: {str(e)}")
                self.update_status("摄像头运行失败")
        
        # 在新线程中运行摄像头
        threading.Thread(target=camera_thread, daemon=True).start()
    
    def detect_face(self):
        """检测人脸关键点"""
        if self.current_image is None:
            return
        
        try:
            results = self.face_mesh.process(self.current_image)
            if results.multi_face_landmarks:
                self.current_landmarks = results.multi_face_landmarks[0]
                self.update_status("人脸检测成功")
            else:
                self.update_status("未检测到人脸")
                self.current_landmarks = None
        except Exception as e:
            self.update_status(f"人脸检测失败: {str(e)}")
            self.current_landmarks = None
    
    def display_image(self, image):
        """显示图片"""
        try:
            # 调整图片大小以适应显示区域
            height, width = image.shape[:2]
            max_width = 800
            max_height = 600
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # 如果需要显示人脸关键点
            if self.show_landmarks and self.current_landmarks is not None:
                image = self.draw_face_landmarks(image)
            
            # 转换为PIL图片
            pil_image = Image.fromarray(image)
            photo = ImageTk.PhotoImage(pil_image)
            
            # 更新显示
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # 保持引用
            
        except Exception as e:
            self.update_status(f"显示图片失败: {str(e)}")
    
    def apply_makeup(self):
        """应用脸谱效果"""
        if self.current_image is None:
            messagebox.showwarning("警告", "请先选择图片")
            return
        
        if self.current_landmarks is None:
            messagebox.showwarning("警告", "未检测到人脸，请选择包含人脸的图片")
            return
        
        try:
            result_image = self.apply_makeup_to_image(self.current_image.copy())
            self.display_image(result_image)
            self.update_status("脸谱效果已应用")
        except Exception as e:
            messagebox.showerror("错误", f"应用脸谱失败: {str(e)}")
    
    def apply_makeup_to_image(self, image):
        """在图片上应用脸谱效果"""
        if self.current_landmarks is None or self.current_makeup_type == "none":
            return image
        
        makeup_pattern = self.makeup_patterns.get(self.current_makeup_type)
        if not makeup_pattern:
            return image
        
        # 创建画布
        canvas = image.copy()
        height, width = canvas.shape[:2]
        
        # 获取关键点坐标
        landmarks = self.current_landmarks.landmark
        
        # 应用脸谱效果
        self.draw_face_outline(canvas, landmarks, makeup_pattern, width, height)
        self.draw_eyebrows(canvas, landmarks, makeup_pattern, width, height)
        self.draw_eye_decoration(canvas, landmarks, makeup_pattern, width, height)
        self.draw_blush(canvas, landmarks, makeup_pattern, width, height)
        
        return canvas
    
    def draw_face_outline(self, canvas, landmarks, pattern, width, height):
        """绘制面部轮廓"""
        face_outline = pattern["pattern"]["faceOutline"]
        if not face_outline:
            return
        
        # 获取面部关键点
        face_points = [
            landmarks[10], landmarks[338], landmarks[297], landmarks[332],
            landmarks[284], landmarks[251], landmarks[389], landmarks[356],
            landmarks[454], landmarks[323], landmarks[361], landmarks[288],
            landmarks[397], landmarks[365], landmarks[379], landmarks[378],
            landmarks[400], landmarks[377], landmarks[152], landmarks[148],
            landmarks[176], landmarks[149], landmarks[150], landmarks[136],
            landmarks[172], landmarks[58], landmarks[132], landmarks[93],
            landmarks[234], landmarks[127], landmarks[162], landmarks[21],
            landmarks[54], landmarks[103], landmarks[67], landmarks[109]
        ]
        
        # 转换为像素坐标
        points = []
        for point in face_points:
            x = int(point.x * width)
            y = int(point.y * height)
            points.append([x, y])
        
        points = np.array(points, dtype=np.int32)
        
        # 创建渐变遮罩
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, [points], 255)
        
        # 应用高斯模糊
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        
        # 创建颜色遮罩
        color = self.hex_to_bgr(face_outline["color"])
        opacity = face_outline.get("opacity", 0.5) * self.opacity
        
        color_mask = np.zeros_like(canvas)
        color_mask[mask > 0] = color
        
        # 混合颜色
        canvas = cv2.addWeighted(canvas, 1 - opacity, color_mask, opacity, 0)
        
        return canvas
    
    def draw_eyebrows(self, canvas, landmarks, pattern, width, height):
        """绘制眉毛"""
        eyebrows_config = pattern["pattern"]["eyebrows"]
        if not eyebrows_config:
            return
        
        # 左眉关键点
        left_brow_points = [70, 107, 66, 105, 63, 70]
        # 右眉关键点  
        right_brow_points = [300, 336, 296, 334, 293, 300]
        
        color = self.hex_to_bgr(eyebrows_config["color"])
        thickness = int(eyebrows_config["thickness"] * self.intensity)
        
        # 绘制左眉
        self.draw_eyebrow_shape(canvas, landmarks, left_brow_points, color, thickness, width, height)
        # 绘制右眉
        self.draw_eyebrow_shape(canvas, landmarks, right_brow_points, color, thickness, width, height)
    
    def draw_eyebrow_shape(self, canvas, landmarks, brow_indices, color, thickness, width, height):
        """绘制眉毛形状"""
        points = []
        for idx in brow_indices:
            point = landmarks[idx]
            x = int(point.x * width)
            y = int(point.y * height)
            points.append([x, y])
        
        points = np.array(points, dtype=np.int32)
        
        # 绘制眉毛线条
        for i in range(len(points) - 1):
            cv2.line(canvas, tuple(points[i]), tuple(points[i + 1]), color, thickness)
    
    def draw_eye_decoration(self, canvas, landmarks, pattern, width, height):
        """绘制眼部装饰"""
        eye_config = pattern["pattern"]["eyeDecoration"]
        if not eye_config:
            return
        
        # 左眼关键点
        left_eye_points = [33, 133, 155, 154, 153, 145, 144, 163]
        # 右眼关键点
        right_eye_points = [263, 362, 384, 385, 386, 387, 388, 390]
        
        color = self.hex_to_bgr(eye_config["color"])
        thickness = int(eye_config["thickness"] * self.intensity)
        
        # 绘制左眼装饰
        self.draw_eye_makeup(canvas, landmarks, left_eye_points, color, thickness, width, height)
        # 绘制右眼装饰
        self.draw_eye_makeup(canvas, landmarks, right_eye_points, color, thickness, width, height)
    
    def draw_eye_makeup(self, canvas, landmarks, eye_indices, color, thickness, width, height):
        """绘制眼部妆容"""
        points = []
        for idx in eye_indices:
            point = landmarks[idx]
            x = int(point.x * width)
            y = int(point.y * height)
            points.append([x, y])
        
        points = np.array(points, dtype=np.int32)
        
        # 绘制眼线
        for i in range(len(points) - 1):
            cv2.line(canvas, tuple(points[i]), tuple(points[i + 1]), color, thickness)
    
    def draw_blush(self, canvas, landmarks, pattern, width, height):
        """绘制腮红"""
        blush_config = pattern["pattern"]["blush"]
        if not blush_config:
            return
        
        # 左脸颊和右脸颊
        left_cheek = landmarks[234]
        right_cheek = landmarks[454]
        
        color = self.hex_to_bgr(blush_config["color"])
        size = int(blush_config["size"] * self.intensity)
        opacity = blush_config.get("opacity", 0.5) * self.opacity
        
        # 绘制左脸颊腮红
        self.draw_blush_circle(canvas, left_cheek, color, size, opacity, width, height)
        # 绘制右脸颊腮红
        self.draw_blush_circle(canvas, right_cheek, color, size, opacity, width, height)
    
    def draw_blush_circle(self, canvas, landmark, color, size, opacity, width, height):
        """绘制腮红圆圈"""
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        
        # 创建遮罩
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(mask, (x, y), size, 255, -1)
        
        # 应用高斯模糊
        mask = cv2.GaussianBlur(mask, (size, size), 0)
        
        # 创建颜色遮罩
        color_mask = np.zeros_like(canvas)
        color_mask[mask > 0] = color
        
        # 混合颜色
        canvas = cv2.addWeighted(canvas, 1 - opacity, color_mask, opacity, 0)
    
    def draw_face_landmarks(self, image):
        """绘制人脸关键点和轮廓"""
        if self.current_landmarks is None:
            return image
        
        canvas = image.copy()
        height, width = canvas.shape[:2]
        landmarks = self.current_landmarks.landmark
        
        # 绘制面部轮廓
        face_outline = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
            397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
        ]
        
        # 绘制面部轮廓线
        cv2.polylines(canvas, [self.get_landmark_points(landmarks, face_outline, width, height)], 
                     True, (0, 255, 0), 2)
        
        # 绘制关键点
        for i in range(0, len(landmarks), 10):  # 每10个点绘制一个
            point = landmarks[i]
            x = int(point.x * width)
            y = int(point.y * height)
            cv2.circle(canvas, (x, y), 2, (0, 255, 0), -1)
        
        # 绘制眼部轮廓
        left_eye = [33, 133, 155, 154, 153, 145, 144, 163]
        right_eye = [263, 362, 384, 385, 386, 387, 388, 390]
        
        cv2.polylines(canvas, [self.get_landmark_points(landmarks, left_eye, width, height)], 
                     True, (255, 0, 0), 2)
        cv2.polylines(canvas, [self.get_landmark_points(landmarks, right_eye, width, height)], 
                     True, (255, 0, 0), 2)
        
        # 绘制嘴部轮廓
        mouth = [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82]
        cv2.polylines(canvas, [self.get_landmark_points(landmarks, mouth, width, height)], 
                     True, (0, 0, 255), 2)
        
        return canvas
    
    def get_landmark_points(self, landmarks, indices, width, height):
        """获取指定索引的关键点坐标"""
        points = []
        for idx in indices:
            point = landmarks[idx]
            x = int(point.x * width)
            y = int(point.y * height)
            points.append([x, y])
        return np.array(points, dtype=np.int32)
    
    def on_show_landmarks_change(self):
        """显示人脸关键点设置改变"""
        self.show_landmarks = self.show_landmarks_var.get()
        # 立即更新显示
        if self.current_image is not None:
            self.display_image(self.current_image)
    
    def on_save_with_landmarks_change(self):
        """保存时包含关键点设置改变"""
        self.save_with_landmarks = self.save_with_landmarks_var.get()
    
    def hex_to_bgr(self, hex_color):
        """将十六进制颜色转换为BGR格式"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (b, g, r)  # OpenCV使用BGR格式
    
    def save_image(self):
        """保存图片"""
        if self.current_image is None:
            messagebox.showwarning("警告", "没有可保存的图片")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 应用当前脸谱效果
                result_image = self.apply_makeup_to_image(self.current_image.copy())
                
                # 如果需要保存关键点，则添加到保存的图片中
                if self.save_with_landmarks and self.current_landmarks is not None:
                    result_image = self.draw_face_landmarks(result_image)
                
                # 转换颜色空间
                result_bgr = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
                
                # 保存图片
                cv2.imwrite(file_path, result_bgr)
                self.update_status(f"图片已保存: {os.path.basename(file_path)}")
                messagebox.showinfo("成功", "图片保存成功！")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存图片失败: {str(e)}")
    
    def reset_effects(self):
        """重置效果"""
        self.makeup_var.set("none")
        self.opacity_var.set(80)
        self.intensity_var.set(100)
        self.offset_var.set(0)
        
        if self.current_image is not None:
            self.display_image(self.current_image)
        
        self.update_status("效果已重置")
    
    def on_makeup_change(self):
        """脸谱类型改变"""
        self.current_makeup_type = self.makeup_var.get()
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def on_opacity_change(self, value):
        """透明度改变"""
        self.opacity = float(value) / 100.0
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def on_intensity_change(self, value):
        """颜色强度改变"""
        self.intensity = float(value) / 100.0
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def on_offset_change(self, value):
        """位置偏移改变"""
        self.offset = int(value)
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

def main():
    """主函数"""
    root = tk.Tk()
    app = PekingOperaDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
