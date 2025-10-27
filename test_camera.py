#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头测试脚本
用于诊断摄像头问题
"""

import cv2
import sys
import time

def test_camera():
    """测试摄像头功能"""
    print("摄像头测试开始...")
    print("=" * 40)
    
    # 测试摄像头设备
    print("1. 检测摄像头设备...")
    for i in range(5):  # 测试前5个设备
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"   ✅ 找到摄像头设备 {i}")
            ret, frame = cap.read()
            if ret:
                print(f"   ✅ 设备 {i} 可以正常读取")
                height, width = frame.shape[:2]
                print(f"   📐 分辨率: {width}x{height}")
            else:
                print(f"   ❌ 设备 {i} 无法读取帧")
            cap.release()
        else:
            print(f"   ❌ 设备 {i} 不可用")
    
    print("\n2. 测试默认摄像头 (设备0)...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("   ❌ 无法打开默认摄像头")
        print("\n可能的原因:")
        print("   - 摄像头被其他程序占用")
        print("   - 摄像头驱动问题")
        print("   - 权限问题")
        return False
    
    print("   ✅ 默认摄像头可以打开")
    
    # 设置摄像头参数
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("   📐 摄像头参数:")
    print(f"     宽度: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"     高度: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    print(f"     FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    
    print("\n3. 测试实时读取...")
    print("   按 'q' 键退出测试")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("   ❌ 无法读取摄像头帧")
                break
            
            frame_count += 1
            
            # 显示帧率
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"   📊 当前FPS: {fps:.1f}")
            
            # 显示图像
            cv2.imshow('摄像头测试 - 按 q 退出', frame)
            
            # 检查退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n   用户中断测试")
    except Exception as e:
        print(f"   ❌ 测试过程中出错: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    elapsed = time.time() - start_time
    if frame_count > 0:
        avg_fps = frame_count / elapsed
        print(f"\n   📊 平均FPS: {avg_fps:.1f}")
        print(f"   📊 总帧数: {frame_count}")
        print(f"   ⏱️  运行时间: {elapsed:.1f}秒")
    
    print("\n4. 测试完成!")
    return True

def main():
    """主函数"""
    print("摄像头功能测试工具")
    print("用于诊断京剧脸谱系统的摄像头问题")
    print()
    
    # 检查OpenCV版本
    print(f"OpenCV版本: {cv2.__version__}")
    
    # 运行测试
    success = test_camera()
    
    if success:
        print("\n✅ 摄像头测试通过！")
        print("如果京剧脸谱系统仍有问题，请检查:")
        print("1. 是否有其他程序占用摄像头")
        print("2. 摄像头权限设置")
        print("3. 系统兼容性")
    else:
        print("\n❌ 摄像头测试失败！")
        print("请检查摄像头连接和驱动")
    
    print("\n按任意键退出...")
    input()

if __name__ == "__main__":
    main()
