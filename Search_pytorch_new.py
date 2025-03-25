import threading
import time
from collections import deque
import mss
import cv2
import numpy as np
from ultralytics import YOLO
import torch

# 全局变量和锁
detection_results = deque(maxlen=20)
lock = threading.Lock()
model = YOLO('best.pt')
screen_region = None

# 检测是否可以使用CUDA
USE_CUDA = torch.cuda.is_available()
if USE_CUDA:
    model.to('cuda')
    model.model.half()  # 使用FP16
    torch.cuda.set_device(0)
else:
    print("CUDA不可用，使用CPU进行推理")

def producer():
    """生产者线程：实时检测并存储结果"""
    print("生产者线程启动...")
    try:
        with mss.mss() as sct:
            # 预分配内存
            last_frame = None
            frame_count = 0
            fps_time = time.time()
            
            while True:
                start_time = time.time()
                
                # 获取截图
                screenshot = np.asarray(sct.grab(screen_region))
                
                # 优化帧处理
                if last_frame is None:
                    frame_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2RGB)
                    last_frame = frame_rgb
                else:
                    # 检查新帧是否有显著变化
                    if np.mean(np.abs(screenshot[:,:,:3] - last_frame)) > 5:
                        frame_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2RGB)
                        last_frame = frame_rgb
                    else:
                        frame_rgb = last_frame

                # YOLO推理配置
                if USE_CUDA:
                    results = model(frame_rgb, 
                                  stream=True,
                                  verbose=False,
                                  conf=0.5,
                                  iou=0.5,
                                  max_det=10,
                                  half=True,
                                  device=0)
                else:
                    results = model(frame_rgb, 
                                  stream=True,
                                  verbose=False,
                                  conf=0.5,
                                  iou=0.5,
                                  max_det=10)
                
                # 处理检测结果
                current_detections = []
                for result in results:
                    boxes = result.boxes
                    if len(boxes) > 0:
                        # 批量处理所有检测结果
                        classes = boxes.cls.cpu().numpy() if USE_CUDA else boxes.cls.numpy()
                        confs = boxes.conf.cpu().numpy() if USE_CUDA else boxes.conf.numpy()
                        coords = boxes.xyxy.cpu().numpy() if USE_CUDA else boxes.xyxy.numpy()
                        
                        for cls, conf, coord in zip(classes, confs, coords):
                            current_detections.append({
                                "类别": result.names[int(cls)],
                                "相似度": f"{conf:.2f}",
                                "坐标": coord.tolist()
                            })
                
                # 更新检测结果
                with lock:
                    detection_results.append(current_detections)
                
                # FPS计算和显示
                frame_count += 1
                if time.time() - fps_time >= 1.0:
                    fps = frame_count / (time.time() - fps_time)
                    frame_count = 0
                    fps_time = time.time()
                
                # 性能输出
                elapsed = time.time() - start_time
                if len(current_detections) > 0:
                    print(f"生产者: 检测到 {len(current_detections)} 个目标, 耗时: {elapsed:.3f}秒, FPS: {fps:.1f}")

                # 动态休眠
                target_fps = 30  # CPU模式下降低目标FPS
                sleep_time = max(0, 1.0/target_fps - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

    except Exception as e:
        print(f"生产者线程发生错误: {str(e)}")
        raise



def select_screen_region():
    """让用户通过鼠标选择屏幕区域"""
    print("请按住鼠标左键并拖动来选择检测区域，选择完成后按回车键确认...")
    
    # 获取全屏截图
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 主显示器
        screenshot = sct.grab(monitor)
        screen = np.array(screenshot)
        screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
    
    # 存储矩形选择的起点和终点
    rect_points = []
    drawing = False
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, rect_points, screen
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            rect_points = [(x, y)]
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                screen_copy = screen.copy()
                cv2.rectangle(screen_copy, rect_points[0], (x, y), (0, 255, 0), 2)
                cv2.imshow('Select Region', screen_copy)
                
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            rect_points.append((x, y))
            screen_copy = screen.copy()
            cv2.rectangle(screen_copy, rect_points[0], rect_points[1], (0, 255, 0), 2)
            cv2.imshow('Select Region', screen_copy)
    
    # 创建窗口和鼠标回调
    cv2.namedWindow('Select Region')
    cv2.setMouseCallback('Select Region', mouse_callback)
    cv2.imshow('Select Region', screen)
    
    # 等待用户确认选择
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter key
            break
    
    cv2.destroyAllWindows()
    
    if len(rect_points) == 2:
        # 确保左上和右下点的正确顺序
        x1, y1 = rect_points[0]
        x2, y2 = rect_points[1]
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return {"left": left, "top": top, "width": width, "height": height}
    
    return None



def consumer():
    """消费者线程：每20ms读取最新检测结果"""
    print("消费者线程启动...")    
    while True:
        try:
            with lock:
                if detection_results:
                    current_detections = list(detection_results)[-1]
                    if current_detections:
                        print(f"消费者: 获取到 {len(current_detections)} 个目标")
            time.sleep(0.02)
        except Exception as e:
            print(f"消费者线程发生错误: {str(e)}")
            raise

if __name__ == "__main__":
    # 加载YOLO模型
    print(f"正在加载YOLO模型: {model.model.names}")
    
    # 让用户选择检测区域
    screen_region = select_screen_region()
    if not screen_region:
        print("未选择有效区域，程序退出")
        exit(1)
    
    print(f"已选择区域: {screen_region}")
    
    # 启动线程
    thread1 = threading.Thread(target=producer, daemon=True)
    thread2 = threading.Thread(target=consumer, daemon=True)
    
    thread1.start()
    thread2.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("正在退出程序...")