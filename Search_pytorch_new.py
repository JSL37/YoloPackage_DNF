import threading
import time
from collections import deque
import mss
import cv2
import numpy as np
from ultralytics import YOLO
import tkinter as tk
from tkinter import ttk
import queue

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

                # 目标检测 控制台输出识别结果
                results = self.model(quyujieping2, stream=True, verbose=True)
                # 目标检测 控制台屏蔽输出识别结果
                # results = self.model(quyujieping2, stream=True, verbose=False)
                
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

# 全局变量
role = []
log_queue = queue.Queue()

class StatusWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("状态监控")
        self.geometry("1200x600")  # 加宽窗口以适应三个文本框
        
        # 初始化线程变量
        self.detection_thread = None
        self.monitor_thread = None
        self.fighting_thread = None
        
        # 创建主容器
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮区域
        self.button_frame = ttk.Frame(self.main_container)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建关闭按钮
        self.close_button = ttk.Button(
            self.button_frame, 
            text="关闭程序", 
            command=self.close_application
        )
        self.close_button.pack(side=tk.RIGHT)
        
        # 创建三分隔面板
        self.paned = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧日志区域
        self.log_frame = ttk.LabelFrame(self.paned, text="系统日志")
        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.paned.add(self.log_frame, weight=1)
        
        # 中间状态区域
        self.status_frame = ttk.LabelFrame(self.paned, text="角色状态")
        self.status_text = tk.Text(self.status_frame, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.paned.add(self.status_frame, weight=1)
        
        # 右侧战斗日志区域
        self.battle_frame = ttk.LabelFrame(self.paned, text="战斗日志")
        self.battle_text = tk.Text(self.battle_frame, wrap=tk.WORD)
        self.battle_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.paned.add(self.battle_frame, weight=1)
        
        # 标记程序是否应该继续运行
        self.should_run = True
        
        # 开始更新循环
        self.update_display()
        
        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.close_application)

    def set_threads(self, detection_thread, monitor_thread):
        """设置需要管理的线程"""
        self.detection_thread = detection_thread
        self.monitor_thread = monitor_thread

    def close_application(self):
        """关闭应用程序的方法"""
        self.should_run = False
        
        # 停止所有线程
        if self.detection_thread:
            self.detection_thread.stop()
        if self.monitor_thread:
            self.monitor_thread.stop()
            
        # 等待线程结束
        if self.detection_thread:
            self.detection_thread.join()
        if self.monitor_thread:
            self.monitor_thread.join()
            
        # 关闭所有OpenCV窗口
        cv2.destroyAllWindows()
        
        # 销毁主窗口
        self.destroy()

    def update_display(self):
        if not self.should_run:
            return
            
        # 更新日志
        while not log_queue.empty():
            log = log_queue.get()
            self.log_text.insert(tk.END, log + "\n")
            self.log_text.see(tk.END)
        
        # 更新状态
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "角色状态:\n")
        for status in role:
            self.status_text.insert(tk.END, f"- {status}\n")
            
        # 更新战斗日志
        while not battle_queue.empty():
            battle_log = battle_queue.get()
            self.battle_text.insert(tk.END, battle_log + "\n")
            self.battle_text.see(tk.END)
        
        # 每100ms更新一次
        self.after(100, self.update_display)

class MonitorThread(threading.Thread):
    def __init__(self, shared_results, interval=1.0):
        super().__init__()
        self.shared_results = shared_results
        self.interval = interval
        self.running = True
        self.map_count = 0
        self.result_count = 0
        self.fighting_thread = FightingThread(shared_results)
    
    def run(self):
        while self.running:
            try:
                results = self.shared_results.get_results()
                
                # 输出所有检测结果
                if results and results[-1]:
                    latest_result = results[-1]
                    if latest_result:  # 确保有检测结果
                        log_msg = "检测结果:\n"
                        for item in latest_result:
                            log_msg += f"- {item['类别']} (相似度: {item['相似度']})\n"
                        log_queue.put(log_msg)
                
                if results:
                    recent_results = results[-10:]
                    map_count = sum(
                        1 for result in recent_results 
                        for item in result 
                        if item['类别'] == '小地图'
                    )
                    if map_count >= 3:
                        if '进图状态' not in role:
                            role.append('进图状态')
                            log_queue.put("检测到进图状态")
                            # 激活战斗线程
                            self.fighting_thread.start_fighting()
                    # else:
                    #     if '进图状态' in role:
                    #         role.remove('进图状态')
                    #         log_queue.put("退出进图状态")
                    #         # 停止战斗线程
                    #         self.fighting_thread.stop_fighting()
                
                time.sleep(self.interval)
            except Exception as e:
                if self.running:
                    print(f"监控线程发生错误: {e}")
                    log_queue.put(f"监控线程发生错误: {e}")
                break
    
    def stop(self):
        """停止线程的方法"""
        self.running = False
        if hasattr(self, 'fighting_thread'):
            self.fighting_thread.stop_fighting()
# 添加新的全局队列用于战斗日志
battle_queue = queue.Queue()

class FightingThread(threading.Thread):
    def __init__(self, shared_results):
        super().__init__()
        self.shared_results = shared_results
        self.running = False
    
    def start_fighting(self):
        """开始战斗"""
        self.running = True
        if not self.is_alive():
            self.start()
    
    def stop_fighting(self):
        """停止战斗"""
        self.running = False
    
    def run(self):
        while self.running:
            try:
                # 在这里添加战斗逻辑
                battle_queue.put("执行战斗操作...")
                time.sleep(0.5)  # 控制战斗操作频率
            except Exception as e:
                battle_queue.put(f"战斗线程错误: {e}")
                break



def main():
    # 创建共享结果对象
    shared_results = DetectionResult(max_size=10)
    
    # 创建状态窗口
    status_window = StatusWindow()
    
    # 创建并启动检测线程
    detection_thread = DetectionThread(shared_results)
    detection_thread.start()
    
    # 创建并启动监控线程
    monitor_thread = MonitorThread(shared_results)
    monitor_thread.start()
    
    # 设置线程到窗口对象
    status_window.set_threads(detection_thread, monitor_thread)
    
    try:
        # 运行主窗口循环
        status_window.mainloop()
    except Exception as e:
        print(f"程序发生错误: {e}")
    finally:
        print("正在停止程序...")
        # 确保线程都被正确停止
        detection_thread.stop()
        monitor_thread.stop()
        detection_thread.join()
        monitor_thread.join()
        # 确保所有OpenCV窗口都被关闭
        cv2.destroyAllWindows()

        
if __name__ == "__main__":
    main()