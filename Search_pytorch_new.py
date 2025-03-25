import threading
import time
from collections import deque
import mss
import cv2
import numpy as np
from ultralytics import YOLO

class DetectionResult:
    def __init__(self, max_size=10):
        self.results = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add_result(self, result):
        with self.lock:
            self.results.append(result)
    
    def get_results(self):
        with self.lock:
            return list(self.results)

class RegionSelector:
    def __init__(self):
        self.drawing = False
        self.x1, self.y1 = -1, -1
        self.x2, self.y2 = -1, -1
        self.selected = False
    
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.x1, self.y1 = x, y
            self.x2, self.y2 = x, y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.x2, self.y2 = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.x2, self.y2 = x, y
    
    def select_region(self):
        # 获取全屏截图
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 主显示器
            screenshot = np.array(sct.grab(monitor))
            
        # 创建窗口和回调
        cv2.namedWindow('Select Region')
        cv2.setMouseCallback('Select Region', self.mouse_callback)
        
        while True:
            img = screenshot.copy()
            if self.x1 != -1 and self.y1 != -1:
                cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2)
            
            cv2.imshow('Select Region', img)
            key = cv2.waitKey(1) & 0xFF
            
            # 按回车确认选择
            if key == 13:  # Enter key
                cv2.destroyWindow('Select Region')
                # 确保坐标为正值
                x1, x2 = min(self.x1, self.x2), max(self.x1, self.x2)
                y1, y2 = min(self.y1, self.y2), max(self.y1, self.y2)
                return {
                    "left": x1,
                    "top": y1,
                    "width": x2 - x1,
                    "height": y2 - y1
                }
            # 按ESC取消选择，使用默认值
            elif key == 27:  # ESC key
                cv2.destroyWindow('Select Region')
                return {"left": 1215, "top": 511, "width": 700, "height": 500}

class DetectionThread(threading.Thread):
    def __init__(self, shared_results):
        super().__init__()
        self.shared_results = shared_results
        self.running = True
        self.model = YOLO('best.pt')
        
        # 在初始化时选择区域
        print("请用鼠标拖动选择检测区域，按回车确认，按ESC使用默认区域")
        region_selector = RegionSelector()
        self.quyu = region_selector.select_region()
        print(f"已选择区域: {self.quyu}")
        
    def run(self):
        with mss.mss() as sct:
            while self.running:
                # 获取区域截屏
                quyujieping = sct.grab(self.quyu)
                quyujieping = np.array(quyujieping)
                quyujieping2 = cv2.cvtColor(quyujieping, cv2.COLOR_BGRA2RGB)

                # 目标检测
                results = self.model(quyujieping2, stream=True, verbose=True)
                
                tuili_jieguo = []
                for result in results:
                    if len(result.boxes.cls) > 0:
                        for i in range(len(result.boxes.cls)):
                            leibie_id = int(result.boxes.cls[i].item())
                            leibie = result.names[leibie_id]
                            xiangsidu = str(result.boxes.conf[i].item())[0:3]
                            zuobiao = result.boxes.xyxy[i].tolist()
                            tuili_jieguo.append({
                                "类别": leibie,
                                "相似度": xiangsidu,
                                "坐标": zuobiao
                            })
                
                # 将结果存入共享对象
                self.shared_results.add_result(tuili_jieguo)
                
                # 显示检测结果
                if len(tuili_jieguo) > 0:
                    for i in tuili_jieguo:
                        cv2.rectangle(
                            quyujieping,
                            (int(i["坐标"][0]), int(i["坐标"][1])),
                            (int(i["坐标"][2]), int(i["坐标"][3])),
                            (0, 255, 0),
                            2
                        )
                        
                        cv2.putText(
                            quyujieping,
                            f"{i['类别']}",
                            (int(i["坐标"][0]), int(i["坐标"][1]) + 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA
                        )
                        
                        cv2.putText(
                            quyujieping,
                            f"{i['相似度']}",
                            (int(i["坐标"][0]) + 80, int(i["坐标"][1]) + 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA
                        )
                
                cv2.imshow("video", quyujieping)
                
                if cv2.waitKey(5) & 0xFF == ord("q"):
                    self.running = False
                    cv2.destroyAllWindows()
                    break
    
    def stop(self):
        self.running = False

class MonitorThread(threading.Thread):
    def __init__(self, shared_results, interval=1.0):
        super().__init__()
        self.shared_results = shared_results
        self.interval = interval
        self.running = True
        
    def run(self):
        while self.running:
            results = self.shared_results.get_results()
            print(f"当前存储的检测结果数量: {len(results)}")
            print(f"最新的检测结果: {results[-1] if results else '无'}")
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False

def main():
    # 创建共享结果对象
    shared_results = DetectionResult(max_size=10)
    
    # 创建并启动检测线程
    detection_thread = DetectionThread(shared_results)
    detection_thread.start()
    
    # 创建并启动监控线程
    monitor_thread = MonitorThread(shared_results)
    monitor_thread.start()
    
    try:
        # 等待检测线程结束
        detection_thread.join()
    except KeyboardInterrupt:
        print("正在停止程序...")
    finally:
        # 停止所有线程
        detection_thread.stop()
        monitor_thread.stop()
        detection_thread.join()
        monitor_thread.join()

if __name__ == "__main__":
    main()