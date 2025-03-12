import cv2
import numpy as np
import time
from PIL import ImageGrab
import os
import tkinter as tk
from tkinter import ttk, filedialog

# 全局变量
roi_selected = False
roi_x, roi_y, roi_w, roi_h = 0, 0, 0, 0
is_running = False
model = None
input_width, input_height = 640, 640  # 默认ONNX模型输入尺寸
classes = []  # 类别列表


def load_model(model_path):
    """加载ONNX模型"""
    global model, classes

    # 检查模型文件是否存在
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件 {model_path} 不存在！请确保模型文件在正确的位置。")

    # 加载类别名称（如果存在）
    class_file = os.path.join(os.path.dirname(model_path), "classes.txt")
    if os.path.exists(class_file):
        with open(class_file, 'r', encoding='utf-8') as f:
            classes = [line.strip() for line in f.readlines()]
    else:
        # 使用默认的COCO类别
        classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
                   'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
                   'horse',
                   'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                   'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
                   'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
                   'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut',
                   'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
                   'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book',
                   'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

    # 加载ONNX模型
    print("正在加载ONNX模型...")
    net = cv2.dnn.readNetFromONNX(model_path)

    # 检查可用的后端并设置首选项
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        print("使用CUDA后端")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    else:
        print("使用CPU后端")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    model = net
    print(f"模型已加载，类别数量: {len(classes)}")
    return net


def select_model():
    """打开文件对话框选择ONNX模型"""
    model_path = filedialog.askopenfilename(
        title="选择ONNX模型文件",
        filetypes=[("ONNX Models", "*.onnx"), ("All Files", "*.*")]
    )
    if model_path:
        try:
            load_model(model_path)
            model_label.config(text=f"已加载模型: {os.path.basename(model_path)}")
            select_roi_button.config(state=tk.NORMAL)
        except Exception as e:
            model_label.config(text=f"模型加载失败: {str(e)}")


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


def preprocess_image(img):
    """预处理图像用于ONNX模型推理"""
    # 调整图像大小
    blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (input_width, input_height),
                                 swapRB=True, crop=False)
    return blob


def post_process(img, outputs, conf_threshold=0.25, nms_threshold=0.45):
    """处理ONNX模型的输出结果"""
    # 初始化结果列表
    class_ids = []
    confidences = []
    boxes = []

    # ONNX模型输出通常是一个包含多个检测结果的数组
    # 每个检测结果通常包含[x, y, w, h, conf, class_scores...]
    img_height, img_width = img.shape[:2]

    # YOLOv5/YOLOv8 ONNX输出格式处理
    output = outputs[0]

    for detection in output:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]

        if confidence > conf_threshold:
            # YOLO返回的是中心坐标和宽高，需要转换为左上角坐标
            cx, cy, w, h = detection[0:4]

            # 将相对坐标转换为绝对坐标
            left = int((cx - w / 2) * img_width)
            top = int((cy - h / 2) * img_height)
            width = int(w * img_width)
            height = int(h * img_height)

            # 添加到结果列表
            class_ids.append(class_id)
            confidences.append(float(confidence))
            boxes.append([left, top, width, height])

    # 执行非极大值抑制
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    results = []
    for i in indices:
        box = boxes[i]
        left, top, width, height = box
        results.append({
            'class_id': class_ids[i],
            'class_name': classes[class_ids[i]] if class_ids[i] < len(classes) else f"未知类别-{class_ids[i]}",
            'confidence': confidences[i],
            'box': [left, top, left + width, top + height]  # [x1, y1, x2, y2]格式
        })

    return results


def draw_detections(img, detections):
    """在图像上绘制检测结果"""
    for detection in detections:
        # 获取检测结果信息
        class_name = detection['class_name']
        confidence = detection['confidence']
        box = detection['box']

        # 绘制边界框
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

        # 绘制标签
        label = f"{class_name} {confidence:.2f}"
        (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (box[0], box[1] - label_height - 5), (box[0] + label_width, box[1]), (0, 255, 0), -1)
        cv2.putText(img, label, (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return img


def process_frame(frame):
    """处理帧并进行检测"""
    # 预处理图像
    blob = preprocess_image(frame)

    # 设置模型输入
    model.setInput(blob)

    # 前向传播
    outputs = model.forward(model.getUnconnectedOutLayersNames())

    # 后处理检测结果
    detections = post_process(frame, outputs, conf_threshold=0.25, nms_threshold=0.45)

    # 绘制检测结果
    result_frame = draw_detections(frame.copy(), detections)

    # 打印检测到的物体和坐标
    if detections:
        print("\n检测结果:")
        for idx, detection in enumerate(detections):
            class_name = detection['class_name']
            confidence = detection['confidence']
            x1, y1, x2, y2 = detection['box']

            # 计算全局坐标（相对于整个屏幕）
            global_x1 = x1 + roi_x
            global_y1 = y1 + roi_y
            global_x2 = x2 + roi_x
            global_y2 = y2 + roi_y

            center_x = (global_x1 + global_x2) / 2
            center_y = (global_y1 + global_y2) / 2

            print(
                f"物体 {idx + 1}: {class_name}, 置信度: {confidence:.2f}, 中心坐标: ({center_x:.1f}, {center_y:.1f}), 边界框: [{global_x1}, {global_y1}, {global_x2}, {global_y2}]")
    else:
        print("未检测到物体")

    return result_frame


def start_detection():
    """开始检测进程"""
    global is_running

    if not model:
        status_label.config(text="请先加载模型")
        return

    if not roi_selected:
        status_label.config(text="请先选择检测区域")
        return

    is_running = True
    status_label.config(text="检测中...")
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    select_roi_button.config(state=tk.DISABLED)
    select_model_button.config(state=tk.DISABLED)

    # 创建一个独立的检测窗口
    cv2.namedWindow('ONNX 区域检测', cv2.WINDOW_NORMAL)

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
            cv2.imshow('ONNX 区域检测', result_frame)

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
        select_model_button.config(state=tk.NORMAL)


def stop_detection():
    """停止检测进程"""
    global is_running
    is_running = False
    status_label.config(text="正在停止...")


# 创建UI
root = tk.Tk()
root.title("ONNX 屏幕区域检测")
root.geometry("550x350")

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# 标题
title_label = ttk.Label(frame, text="ONNX 屏幕区域检测工具", font=("Arial", 16))
title_label.pack(pady=10)

# 选择模型按钮
select_model_button = ttk.Button(frame, text="选择ONNX模型", command=select_model)
select_model_button.pack(pady=5)

# 模型信息
model_label = ttk.Label(frame, text="未加载模型")
model_label.pack(pady=5)

# 选择ROI按钮
select_roi_button = ttk.Button(frame, text="选择检测区域", command=select_roi, state=tk.DISABLED)
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
info_label.pack(pady=5)

# 版权标签
copyright_label = ttk.Label(frame, text="© 2025 ONNX视频检测工具", font=("Arial", 8))
copyright_label.pack(pady=5)

# 启动tkinter主循环
if __name__ == "__main__":
    root.mainloop()