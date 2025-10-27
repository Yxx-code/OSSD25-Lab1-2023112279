#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京剧脸谱虚拟交互体验系统 - 高级桌面版
基于PyQt5的现代化界面，支持图片识别和实时摄像头
"""

import sys
import os
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageQt
import json
from typing import Dict, List, Tuple, Optional
import threading
import time

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                                QSlider, QComboBox, QCheckBox, QFileDialog, 
                                QMessageBox, QGroupBox, QFrame, QProgressBar,
                                QTabWidget, QTextEdit, QSplitter, QScrollArea)
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
    from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon
except ImportError:
    print("错误: 需要安装PyQt5")
    print("请运行: pip install PyQt5")
    sys.exit(1)

class FaceDetectionThread(QThread):
    """人脸检测线程"""
    face_detected = pyqtSignal(object)
    image_updated = pyqtSignal(object)
    
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.running = True
        
    def run(self):
        """运行人脸检测"""
        try:
            # 初始化MediaPipe
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # 检测人脸
            results = face_mesh.process(self.image)
            if results.multi_face_landmarks:
                self.face_detected.emit(results.multi_face_landmarks[0])
            
            self.image_updated.emit(self.image)
            
        except Exception as e:
            print(f"人脸检测错误: {e}")

class CameraThread(QThread):
    """摄像头线程"""
    frame_ready = pyqtSignal(object)
    face_detected = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        
    def start_camera(self):
        """启动摄像头"""
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.running = True
            self.start()
        else:
            self.frame_ready.emit(None)
    
    def stop_camera(self):
        """停止摄像头"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.quit()
        self.wait()
    
    def run(self):
        """运行摄像头循环"""
        try:
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("摄像头读取失败")
                    break
                
                # 转换颜色空间
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 检测人脸
                try:
                    results = face_mesh.process(frame_rgb)
                    if results.multi_face_landmarks:
                        self.face_detected.emit(results.multi_face_landmarks[0])
                except Exception as e:
                    print(f"人脸检测错误: {e}")
                
                self.frame_ready.emit(frame_rgb)
                
                # 控制帧率
                time.sleep(0.033)  # 约30FPS
                
        except Exception as e:
            print(f"摄像头线程错误: {e}")
            self.frame_ready.emit(None)

class PekingOperaAdvancedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.current_landmarks = None
        self.current_makeup_type = "none"
        self.camera_thread = None
        self.face_detection_thread = None
        
        # 脸谱图案数据
        self.makeup_patterns = self.load_makeup_patterns()
        
        # 界面参数
        self.opacity = 0.8
        self.intensity = 1.0
        self.offset = 0
        self.face_tracking = True
        self.edge_smoothing = True
        self.show_landmarks = True
        self.save_with_landmarks = False
        
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("京剧脸谱系统 v2.0 - 高级版")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2F1B14;
                color: #FFE4B5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FFD700;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #FFD700;
            }
            QPushButton {
                background-color: #8B0000;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #CD853F;
            }
            QPushButton:pressed {
                background-color: #A0522D;
            }
            QSlider::groove:horizontal {
                border: 1px solid #FFD700;
                height: 8px;
                background: #1a0f0a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFD700;
                border: 1px solid #8B0000;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QComboBox {
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 5px;
                background-color: #1a0f0a;
                color: #FFE4B5;
            }
            QCheckBox {
                color: #FFE4B5;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #FFD700;
                background-color: #1a0f0a;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #FFD700;
                background-color: #8B0000;
                border-radius: 3px;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧控制面板
        self.create_control_panel(splitter)
        
        # 右侧图片显示区域
        self.create_image_panel(splitter)
        
        # 设置分割器比例
        splitter.setSizes([400, 1000])
        
    def create_control_panel(self, parent):
        """创建控制面板"""
        control_widget = QWidget()
        control_widget.setMaximumWidth(400)
        control_layout = QVBoxLayout(control_widget)
        
        # 标题
        title_label = QLabel("🎭 京剧脸谱体验")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700; margin: 10px;")
        control_layout.addWidget(title_label)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        control_layout.addWidget(tab_widget)
        
        # 图片选择选项卡
        self.create_image_tab(tab_widget)
        
        # 脸谱设置选项卡
        self.create_makeup_tab(tab_widget)
        
        # 参数调节选项卡
        self.create_params_tab(tab_widget)
        
        # 高级设置选项卡
        self.create_advanced_tab(tab_widget)
        
        parent.addWidget(control_widget)
        
    def create_image_tab(self, parent):
        """创建图片选择选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 图片选择组
        image_group = QGroupBox("图片选择")
        image_layout = QVBoxLayout(image_group)
        
        # 选择图片按钮
        select_btn = QPushButton("📁 选择图片文件")
        select_btn.clicked.connect(self.select_image)
        image_layout.addWidget(select_btn)
        
        # 摄像头按钮
        camera_btn = QPushButton("📷 打开摄像头")
        camera_btn.clicked.connect(self.toggle_camera)
        image_layout.addWidget(camera_btn)
        
        # 状态显示
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #00FF00; font-weight: bold;")
        image_layout.addWidget(self.status_label)
        
        layout.addWidget(image_group)
        
        # 操作按钮组
        action_group = QGroupBox("操作")
        action_layout = QVBoxLayout(action_group)
        
        # 应用脸谱按钮
        apply_btn = QPushButton("🎨 应用脸谱")
        apply_btn.clicked.connect(self.apply_makeup)
        action_layout.addWidget(apply_btn)
        
        # 保存图片按钮
        save_btn = QPushButton("💾 保存图片")
        save_btn.clicked.connect(self.save_image)
        action_layout.addWidget(save_btn)
        
        # 重置按钮
        reset_btn = QPushButton("🔄 重置效果")
        reset_btn.clicked.connect(self.reset_effects)
        action_layout.addWidget(reset_btn)
        
        layout.addWidget(action_group)
        layout.addStretch()
        
        parent.addTab(tab, "图片")
        
    def create_makeup_tab(self, parent):
        """创建脸谱设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 脸谱类型组
        makeup_group = QGroupBox("脸谱类型")
        makeup_layout = QVBoxLayout(makeup_group)
        
        # 脸谱类型选择
        self.makeup_combo = QComboBox()
        self.makeup_combo.addItems(["无脸谱", "生角", "旦角", "净角", "丑角"])
        self.makeup_combo.currentTextChanged.connect(self.on_makeup_change)
        makeup_layout.addWidget(self.makeup_combo)
        
        # 脸谱描述
        self.makeup_desc = QTextEdit()
        self.makeup_desc.setMaximumHeight(100)
        self.makeup_desc.setReadOnly(True)
        self.makeup_desc.setStyleSheet("background-color: #1a0f0a; border: 1px solid #FFD700;")
        makeup_layout.addWidget(self.makeup_desc)
        
        layout.addWidget(makeup_group)
        
        # 经典角色组
        character_group = QGroupBox("经典角色")
        character_layout = QVBoxLayout(character_group)
        
        # 角色选择
        self.character_combo = QComboBox()
        self.character_combo.addItems(["自定义", "关羽", "包拯", "曹操"])
        self.character_combo.currentTextChanged.connect(self.on_character_change)
        character_layout.addWidget(self.character_combo)
        
        layout.addWidget(character_group)
        layout.addStretch()
        
        parent.addTab(tab, "脸谱")
        
    def create_params_tab(self, parent):
        """创建参数调节选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 透明度调节
        opacity_group = QGroupBox("透明度")
        opacity_layout = QVBoxLayout(opacity_group)
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self.on_opacity_change)
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel("80%")
        self.opacity_label.setAlignment(Qt.AlignCenter)
        opacity_layout.addWidget(self.opacity_label)
        
        layout.addWidget(opacity_group)
        
        # 颜色强度调节
        intensity_group = QGroupBox("颜色强度")
        intensity_layout = QVBoxLayout(intensity_group)
        
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(100)
        self.intensity_slider.valueChanged.connect(self.on_intensity_change)
        intensity_layout.addWidget(self.intensity_slider)
        
        self.intensity_label = QLabel("100%")
        self.intensity_label.setAlignment(Qt.AlignCenter)
        intensity_layout.addWidget(self.intensity_label)
        
        layout.addWidget(intensity_group)
        
        # 位置偏移调节
        offset_group = QGroupBox("位置偏移")
        offset_layout = QVBoxLayout(offset_group)
        
        self.offset_slider = QSlider(Qt.Horizontal)
        self.offset_slider.setRange(-50, 50)
        self.offset_slider.setValue(0)
        self.offset_slider.valueChanged.connect(self.on_offset_change)
        offset_layout.addWidget(self.offset_slider)
        
        self.offset_label = QLabel("0")
        self.offset_label.setAlignment(Qt.AlignCenter)
        offset_layout.addWidget(self.offset_label)
        
        layout.addWidget(offset_group)
        layout.addStretch()
        
        parent.addTab(tab, "参数")
        
    def create_advanced_tab(self, parent):
        """创建高级设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 检测设置组
        detection_group = QGroupBox("检测设置")
        detection_layout = QVBoxLayout(detection_group)
        
        self.face_tracking_cb = QCheckBox("启用面部跟踪")
        self.face_tracking_cb.setChecked(True)
        self.face_tracking_cb.toggled.connect(self.on_face_tracking_change)
        detection_layout.addWidget(self.face_tracking_cb)
        
        self.edge_smoothing_cb = QCheckBox("边缘平滑处理")
        self.edge_smoothing_cb.setChecked(True)
        self.edge_smoothing_cb.toggled.connect(self.on_edge_smoothing_change)
        detection_layout.addWidget(self.edge_smoothing_cb)
        
        self.show_landmarks_cb = QCheckBox("显示人脸关键点")
        self.show_landmarks_cb.setChecked(True)
        self.show_landmarks_cb.toggled.connect(self.on_show_landmarks_change)
        detection_layout.addWidget(self.show_landmarks_cb)
        
        self.save_with_landmarks_cb = QCheckBox("保存时包含关键点")
        self.save_with_landmarks_cb.setChecked(False)
        self.save_with_landmarks_cb.toggled.connect(self.on_save_with_landmarks_change)
        detection_layout.addWidget(self.save_with_landmarks_cb)
        
        layout.addWidget(detection_group)
        
        # 渲染设置组
        render_group = QGroupBox("渲染设置")
        render_layout = QVBoxLayout(render_group)
        
        # 渲染质量选择
        quality_label = QLabel("渲染质量:")
        render_layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["低", "中", "高", "超高"])
        self.quality_combo.setCurrentText("高")
        render_layout.addWidget(self.quality_combo)
        
        layout.addWidget(render_group)
        
        # 性能监控组
        perf_group = QGroupBox("性能监控")
        perf_layout = QVBoxLayout(perf_group)
        
        self.fps_label = QLabel("FPS: --")
        perf_layout.addWidget(self.fps_label)
        
        self.memory_label = QLabel("内存: --")
        perf_layout.addWidget(self.memory_label)
        
        layout.addWidget(perf_group)
        layout.addStretch()
        
        parent.addTab(tab, "高级")
        
    def create_image_panel(self, parent):
        """创建图片显示面板"""
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        
        # 图片显示标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(800, 600)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #FFD700;
                border-radius: 10px;
                background-color: #1a0f0a;
            }
        """)
        self.image_label.setText("请选择图片或打开摄像头")
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1a0f0a;
            }
        """)
        
        image_layout.addWidget(scroll_area)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        image_layout.addWidget(self.progress_bar)
        
        parent.addWidget(image_widget)
        
    def load_makeup_patterns(self):
        """加载脸谱图案数据"""
        return {
            "sheng": {
                "name": "生角",
                "description": "生角是京剧中的正面男性角色，脸谱相对简洁，突出英俊正直的特征。",
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
                "description": "旦角是女性角色的统称，脸谱注重表现女性的柔美和端庄。",
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
                "description": "净角多为性格鲜明的男性角色，脸谱色彩浓烈，图案复杂，富有表现力。",
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
                "description": "丑角是喜剧角色，脸谱特征鲜明，通常在鼻梁处涂抹白色，形成滑稽的效果。",
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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff);;所有文件 (*.*)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """加载图片"""
        try:
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 不确定进度
            
            # 读取图片
            image = cv2.imread(file_path)
            if image is None:
                QMessageBox.critical(self, "错误", "无法读取图片文件")
                return
            
            # 转换颜色空间
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.current_image = image_rgb
            
            # 显示图片
            self.display_image(image_rgb)
            
            # 启动人脸检测线程
            self.face_detection_thread = FaceDetectionThread(image_rgb)
            self.face_detection_thread.face_detected.connect(self.on_face_detected)
            self.face_detection_thread.image_updated.connect(self.on_image_updated)
            self.face_detection_thread.start()
            
            self.update_status(f"已加载图片: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载图片失败: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def toggle_camera(self):
        """切换摄像头"""
        if self.camera_thread is None or not self.camera_thread.isRunning():
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """启动摄像头"""
        try:
            # 测试摄像头是否可用
            test_cap = cv2.VideoCapture(0)
            if not test_cap.isOpened():
                QMessageBox.warning(self, "警告", "无法打开摄像头，请检查摄像头是否被其他程序占用")
                test_cap.release()
                return
            
            test_cap.release()
            
            self.camera_thread = CameraThread()
            self.camera_thread.frame_ready.connect(self.on_camera_frame)
            self.camera_thread.face_detected.connect(self.on_face_detected)
            self.camera_thread.start_camera()
            
            # 更新按钮文本
            for i in range(self.centralWidget().layout().itemAt(0).widget().layout().itemAt(1).widget().count()):
                tab = self.centralWidget().layout().itemAt(0).widget().layout().itemAt(1).widget().widget(i)
                if tab.objectName() == "image_tab":
                    buttons = tab.findChildren(QPushButton)
                    for btn in buttons:
                        if "摄像头" in btn.text():
                            btn.setText("📷 关闭摄像头")
                            break
                    break
            
            self.update_status("摄像头已启动")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动摄像头失败: {str(e)}")
            self.update_status("摄像头启动失败")
    
    def stop_camera(self):
        """停止摄像头"""
        if self.camera_thread:
            self.camera_thread.stop_camera()
            self.camera_thread = None
        
        # 更新按钮文本
        for i in range(self.centralWidget().layout().itemAt(0).widget().layout().itemAt(1).widget().count()):
            tab = self.centralWidget().layout().itemAt(0).widget().layout().itemAt(1).widget().widget(i)
            if tab.objectName() == "image_tab":
                buttons = tab.findChildren(QPushButton)
                for btn in buttons:
                    if "摄像头" in btn.text():
                        btn.setText("📷 打开摄像头")
                        break
                break
        
        self.update_status("摄像头已关闭")
    
    def on_camera_frame(self, frame):
        """处理摄像头帧"""
        if frame is not None:
            self.current_image = frame
            if self.current_makeup_type != "none" and self.current_landmarks:
                frame = self.apply_makeup_to_image(frame.copy())
            self.display_image(frame)
    
    def on_face_detected(self, landmarks):
        """人脸检测完成"""
        self.current_landmarks = landmarks
        self.update_status("人脸检测成功")
        
        # 自动应用脸谱效果
        if self.current_makeup_type != "none" and self.current_image is not None:
            self.apply_makeup()
    
    def on_image_updated(self, image):
        """图片更新完成"""
        self.display_image(image)
    
    def display_image(self, image):
        """显示图片"""
        try:
            # 调整图片大小
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
            
            # 转换为QImage
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 转换为QPixmap并显示
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"显示图片失败: {e}")
    
    def apply_makeup(self):
        """应用脸谱效果"""
        if self.current_image is None:
            QMessageBox.warning(self, "警告", "请先选择图片")
            return
        
        if self.current_landmarks is None:
            QMessageBox.warning(self, "警告", "未检测到人脸，请选择包含人脸的图片")
            return
        
        try:
            result_image = self.apply_makeup_to_image(self.current_image.copy())
            self.display_image(result_image)
            self.update_status("脸谱效果已应用")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用脸谱失败: {str(e)}")
    
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
            QMessageBox.warning(self, "警告", "没有可保存的图片")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图片",
            f"peking_opera_{self.current_makeup_type}_{int(time.time())}.png",
            "PNG文件 (*.png);;JPEG文件 (*.jpg);;所有文件 (*.*)"
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
                QMessageBox.information(self, "成功", "图片保存成功！")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存图片失败: {str(e)}")
    
    def reset_effects(self):
        """重置效果"""
        self.makeup_combo.setCurrentText("无脸谱")
        self.opacity_slider.setValue(80)
        self.intensity_slider.setValue(100)
        self.offset_slider.setValue(0)
        
        if self.current_image is not None:
            self.display_image(self.current_image)
        
        self.update_status("效果已重置")
    
    def on_makeup_change(self, text):
        """脸谱类型改变"""
        makeup_map = {
            "无脸谱": "none",
            "生角": "sheng",
            "旦角": "dan",
            "净角": "jing",
            "丑角": "chou"
        }
        self.current_makeup_type = makeup_map.get(text, "none")
        
        # 更新描述
        if self.current_makeup_type != "none":
            pattern = self.makeup_patterns.get(self.current_makeup_type)
            if pattern:
                self.makeup_desc.setText(pattern["description"])
        else:
            self.makeup_desc.setText("")
        
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def on_character_change(self, text):
        """经典角色改变"""
        # 这里可以添加经典角色的特殊配置
        pass
    
    def on_opacity_change(self, value):
        """透明度改变"""
        self.opacity = value / 100.0
        self.opacity_label.setText(f"{value}%")
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def on_intensity_change(self, value):
        """颜色强度改变"""
        self.intensity = value / 100.0
        self.intensity_label.setText(f"{value}%")
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def on_offset_change(self, value):
        """位置偏移改变"""
        self.offset = value
        self.offset_label.setText(str(value))
        if self.current_image is not None and self.current_landmarks is not None:
            self.apply_makeup()
    
    def on_face_tracking_change(self, checked):
        """面部跟踪设置改变"""
        self.face_tracking = checked
    
    def on_edge_smoothing_change(self, checked):
        """边缘平滑设置改变"""
        self.edge_smoothing = checked
    
    def on_show_landmarks_change(self, checked):
        """显示人脸关键点设置改变"""
        self.show_landmarks = checked
        # 立即更新显示
        if self.current_image is not None:
            self.display_image(self.current_image)
    
    def on_save_with_landmarks_change(self, checked):
        """保存时包含关键点设置改变"""
        self.save_with_landmarks = checked
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.setText(message)
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop_camera()
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("京剧脸谱系统")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Peking Opera Studio")
    
    # 创建主窗口
    window = PekingOperaAdvancedApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
