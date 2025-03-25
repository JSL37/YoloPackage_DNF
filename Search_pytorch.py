import mss
import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
from collections import deque

# 全局变量和锁
shared_results = deque(maxlen=20)  # 存储最近20次检测结果（200ms数据）
lock = threading.Lock()
stop_event = threading.Event()  # 用于优雅退出线程

# 加载模型（全局初始化）
model = YOLO('best.pt')

# 截屏区域配置
monitor_region = {"left": 1163, "top": 129, "width": 1280, "height": 720}

def producer_thread():
    """生产者线程：实时检测并存储结果"""
    with mss.mss() as sct:
        while not stop_event.is_set():
            start_time = time.time()

            # 截屏和预处理
            screenshot = sct.grab(monitor_region)
            frame = np.array(screenshot)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)

            # YOLO推理
            results = model(frame_rgb, stream=True, verbose=False, max_det=100)

            # 解析检测结果
            detection_result = []
            for result in results:
                if len(result.boxes.cls) > 0:
                    for i in range(len(result.boxes.cls)):
                        cls_id = int(result.boxes.cls[i].item())
                        cls_name = result.names[cls_id]
                        conf = f"{result.boxes.conf[i].item():.2f}"
                        coords = result.boxes.xyxy[i].tolist()
                        detection_result.append({
                            "类别": cls_name,
                            "相似度": conf,
                            "坐标": coords
                        })

            # 将结果存入共享队列
            with lock:
                shared_results.append(detection_result)

            # 控制检测频率（目标：100次/秒 → 10ms间隔）
            elapsed = time.time() - start_time
            sleep_time = 0.01 - elapsed  # 10ms间隔
            if sleep_time > 0:
                time.sleep(sleep_time)

def consumer_thread():
    """消费者线程：分析检测结果并执行动作"""
    while not stop_event.is_set():
        start_time = time.time()

        # 获取最新检测数据（需快速操作）
        with lock:
            current_data = list(shared_results)  # 获取快照

        # 示例：分析最近3帧的检测结果（取最后一个元素）
        if current_data:
            latest_result = current_data[-1]
            # 在此处添加你的游戏控制逻辑，例如：
            # 根据敌人坐标执行攻击/移动指令
            print(f"最新检测结果：{latest_result[:3]}...")  # 只显示前3个检测对象

        # 控制控制频率（目标：50次/秒 → 20ms间隔）
        elapsed = time.time() - start_time
        sleep_time = 0.02 - elapsed  # 20ms间隔
        if sleep_time > 0:
            time.sleep(sleep_time)

def main():
    # 启动线程
    producer = threading.Thread(target=producer_thread)
    consumer = threading.Thread(target=consumer_thread)

    producer.daemon = True
    consumer.daemon = True

    producer.start()
    consumer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping threads...")
        stop_event.set()  # 通知线程退出
        producer.join()
        consumer.join()

if __name__ == "__main__":
    main()