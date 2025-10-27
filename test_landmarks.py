#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试人脸关键点显示功能
"""

import cv2
import numpy as np
import mediapipe as mp
import sys
import os

def test_face_detection(image_path):
    """测试人脸检测和关键点显示"""
    # 初始化MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图片: {image_path}")
        return False
    
    # 转换颜色空间
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 检测人脸
    results = face_mesh.process(image_rgb)
    
    if results.multi_face_landmarks:
        print("✓ 检测到人脸")
        
        # 绘制关键点
        landmarks = results.multi_face_landmarks[0]
        canvas = image_rgb.copy()
        height, width = canvas.shape[:2]
        
        # 绘制面部轮廓
        face_outline = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
            397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
        ]
        
        # 获取轮廓点
        points = []
        for idx in face_outline:
            point = landmarks.landmark[idx]
            x = int(point.x * width)
            y = int(point.y * height)
            points.append([x, y])
        
        points = np.array(points, dtype=np.int32)
        
        # 绘制面部轮廓线
        cv2.polylines(canvas, [points], True, (0, 255, 0), 2)
        
        # 绘制关键点
        for i in range(0, len(landmarks.landmark), 10):
            point = landmarks.landmark[i]
            x = int(point.x * width)
            y = int(point.y * height)
            cv2.circle(canvas, (x, y), 2, (0, 255, 0), -1)
        
        # 绘制眼部轮廓
        left_eye = [33, 133, 155, 154, 153, 145, 144, 163]
        right_eye = [263, 362, 384, 385, 386, 387, 388, 390]
        
        # 左眼
        left_eye_points = []
        for idx in left_eye:
            point = landmarks.landmark[idx]
            x = int(point.x * width)
            y = int(point.y * height)
            left_eye_points.append([x, y])
        left_eye_points = np.array(left_eye_points, dtype=np.int32)
        cv2.polylines(canvas, [left_eye_points], True, (255, 0, 0), 2)
        
        # 右眼
        right_eye_points = []
        for idx in right_eye:
            point = landmarks.landmark[idx]
            x = int(point.x * width)
            y = int(point.y * height)
            right_eye_points.append([x, y])
        right_eye_points = np.array(right_eye_points, dtype=np.int32)
        cv2.polylines(canvas, [right_eye_points], True, (255, 0, 0), 2)
        
        # 绘制嘴部轮廓
        mouth = [13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82]
        mouth_points = []
        for idx in mouth:
            point = landmarks.landmark[idx]
            x = int(point.x * width)
            y = int(point.y * height)
            mouth_points.append([x, y])
        mouth_points = np.array(mouth_points, dtype=np.int32)
        cv2.polylines(canvas, [mouth_points], True, (0, 0, 255), 2)
        
        # 保存结果
        output_path = "test_landmarks_result.jpg"
        result_bgr = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, result_bgr)
        print(f"✓ 结果已保存到: {output_path}")
        
        return True
    else:
        print("✗ 未检测到人脸")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python test_landmarks.py <图片路径>")
        print("示例: python test_landmarks.py test.jpg")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        return
    
    print(f"测试图片: {image_path}")
    print("正在检测人脸关键点...")
    
    success = test_face_detection(image_path)
    
    if success:
        print("✓ 测试成功！")
    else:
        print("✗ 测试失败！")

if __name__ == "__main__":
    main()
