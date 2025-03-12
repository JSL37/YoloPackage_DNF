import cv2
import torch
import numpy as np
import time
from PIL import ImageGrab
import os
import tkinter as tk
from tkinter import ttk

# 全局变量
roi_selected = False
roi_x, roi_y, roi_w, roi_h = 0, 0, 0, 0
is_running = False

# 确保当前路径中有模型文件
model_path = 'yolov5s_best.pt'
if not os.path.exists(model_path):
    raise FileNotFoundError(f"模型文件 {model_path} 不存在！请确保模型文件在正确的位置。")

# 加载YOLOv5模型
print("正在加载模型...")
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
print(f"模型已加载到 {device} 设备")

# 设置模型参数
model.conf = 0.25  # 置信度阈值
model.iou = 0.45   # IoU阈值

def select_roi():
    """打开选择ROI的界面"""
    global roi_selected, roi_x, roi_y, roi_w, roi_h
    
    # 捕获整个屏幕
    img = ImageGrab.grab()
    screen = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # 创建一个窗口用于选择ROI
    cv2.namedWindow('选择检测区域', cv2.WINDOW_NORMAL)
    
    # 调整窗口大小，使其更容易查看
    screen_height, screen_width = screen.shape[:2]
    display_width = min(screen_width, 1280)
    display_height = int(screen_height * (display_width / screen_width))
    cv2.resizeWindow('选择检测区域', display_width, display_height)
    
    # 使用OpenCV的selectROI函数让用户选择区域
    roi = cv2.selectROI('选择检测区域', screen, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow('选择检测区域')
    
    roi_x, roi_y, roi_w, roi_h = roi
    roi_selected = True
    
    # 更新UI信息
    if roi_w > 0 and roi_h > 0:
        roi_info_label.config(text=f"已选择区域: X={roi_x}, Y={roi_y}, 宽={roi_w}, 高={roi_h}")
        start_button.config(state=tk.NORMAL)
    else:
        roi_info_label.config(text="未选择有效区域，请重新选择")
        start_button.config(state=tk.DISABLED)

def screen_capture_roi():
    """捕获选定的屏幕区域"""
    img = ImageGrab.grab(bbox=(roi_x, roi_y, roi_x + roi_w, roi_y + roi_h))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def process_frame(frame):
    """处理帧并进行检测"""
    # 使用模型进行预测
    results = model(frame)
    
    # 获取检测结果
    predictions = results.pandas().xyxy[0]
    
    # 创建一个可写的帧副本
    annotated_frame = results.render()[0].copy()
    
    # 打印检测到的物体和坐标
    if not predictions.empty:
        print("\n检测结果:")
        for idx, row in predictions.iterrows():
            class_name = row['name']
            confidence = row['confidence']
            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            
            # 计算全局坐标（相对于整个屏幕）
            global_x1 = x1 + roi_x
            global_y1 = y1 + roi_y
            global_x2 = x2 + roi_x
            global_y2 = y2 + roi_y
            
            center_x = (global_x1 + global_x2) / 2
            center_y = (global_y1 + global_y2) / 2
            
            print(f"物体 {idx+1}: {class_name}, 置信度: {confidence:.2f}, 中心坐标: ({center_x:.1f}, {center_y:.1f}), 边界框: [{global_x1}, {global_y1}, {global_x2}, {global_y2}]")
    else:
        print("未检测到物体")
        
    return annotated_frame

def start_detection():
    """开始检测进程"""
    global is_running
    
    if not roi_selected:
        status_label.config(text="请先选择检测区域")
        return
    
    is_running = True
    status_label.config(text="检测中...")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    select_roi_button.config(state=tk.DISABLED)
    
    # 创建一个独立的检测窗口
    cv2.namedWindow('YOLOv5 区域检测', cv2.WINDOW_NORMAL)
    
    prev_time = time.time()
    
    try:
        while is_running:
            # 捕获屏幕区域
            frame = screen_capture_roi()
            
            # 处理当前帧
            result_frame = process_frame(frame)
            
            # 计算FPS
            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time
            
            # 显示FPS
            cv2.putText(result_frame, f"FPS: {fps:.1f}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 更新检测窗口
            cv2.imshow('YOLOv5 区域检测', result_frame)
            
            # 按q键退出或检查is_running标志
            if cv2.waitKey(1) & 0xFF == ord('q'):
                is_running = False
                break
                
            # 更新tkinter UI
            root.update()
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        status_label.config(text=f"错误: {str(e)}")
    finally:
        is_running = False
        cv2.destroyAllWindows()
        status_label.config(text="检测已停止")
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        select_roi_button.config(state=tk.NORMAL)

def stop_detection():
    """停止检测进程"""
    global is_running
    is_running = False
    status_label.config(text="正在停止...")

# 创建UI
root = tk.Tk()
root.title("YOLOv5 屏幕区域检测")
root.geometry("500x300")

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# 标题
title_label = ttk.Label(frame, text="YOLOv5 屏幕区域检测工具", font=("Arial", 16))
title_label.pack(pady=10)

# 选择ROI按钮
select_roi_button = ttk.Button(frame, text="选择检测区域", command=select_roi)
select_roi_button.pack(pady=5)

# ROI信息
roi_info_label = ttk.Label(frame, text="未选择检测区域")
roi_info_label.pack(pady=5)

# 按钮框架
button_frame = ttk.Frame(frame)
button_frame.pack(pady=10)

# 开始检测按钮
start_button = ttk.Button(button_frame, text="开始检测", command=start_detection, state=tk.DISABLED)
start_button.grid(row=0, column=0, padx=5)

# 停止检测按钮
stop_button = ttk.Button(button_frame, text="停止检测", command=stop_detection, state=tk.DISABLED)
stop_button.grid(row=0, column=1, padx=5)

# 状态标签
status_label = ttk.Label(frame, text="就绪")
status_label.pack(pady=5)

# 信息标签
info_label = ttk.Label(frame, text="按'q'键可以关闭检测窗口", font=("Arial", 9))
info_label.pack(pady=10)

# 启动tkinter主循环
root.mainloop()