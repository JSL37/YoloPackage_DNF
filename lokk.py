import cv2
import numpy as np
from ultralytics import YOLO
import time
import dxcam  # 替换 mss 为 dxcam

# 加载模型
model = YOLO('best.pt')  # 预训练的YOLOv8n模型

# 定义截屏区域 (left, top, right, bottom) - DxCam 使用不同的格式q
left, top = 1215, 511
width, height = 700, 500
region = (left, top, left + width, top + height)

# 实例化 DxCam
camera = dxcam.create(output_idx=0)  # 使用主显示器
camera.start(region=region, target_fps=60)  # 可以设置目标帧率

try:
    while True:  # 死循环
        # 获取区域截屏
        quyujieping = camera.get_latest_frame()
        if quyujieping is None:
            continue
            
        # DxCam 已经返回 numpy 数组，格式为 RGB
        quyujieping2 = quyujieping.copy()  # RGB 格式用于模型
        quyujieping = cv2.cvtColor(quyujieping, cv2.COLOR_RGB2BGR)  # 转换为 BGR 用于 OpenCV 显示
        
        # 在图片上运行推理
        results = model(quyujieping2, stream=True, verbose=True)
        
        tuili_jieguo = []
        
        # 处理结果生成器
        for result in results:
            if len(result.boxes.cls) > 0:
                for i in range(len(result.boxes.cls)):
                    # 获取类别
                    leibie_id = int(result.boxes.cls[i].item())  # 获取类别Id
                    leibie = result.names[leibie_id]  # 获取类别的名称
                    # 获取相似度
                    xiangsidu = str(result.boxes.conf[i].item())[0:3]
                    # 获取坐标值,2个,左上角和右上角
                    zuobiao = result.boxes.xyxy[i].tolist()
                    # 存入列表中
                    tuili_jieguo.append({"类别": leibie, "相似度": xiangsidu, "坐标": zuobiao})
        
        # 画框
        if len(tuili_jieguo) > 0:
            for i in tuili_jieguo:
                cv2.rectangle(quyujieping, (int(i["坐标"][0]), int(i["坐标"][1])), (int(i["坐标"][2]), int(i["坐标"][3])),
                              (0, 255, 0), 2)
                
                # 标记类别
                cv2.putText(quyujieping, f"{i['类别']}", (int(i["坐标"][0]), int(i["坐标"][1]) + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 1, cv2.LINE_AA)
                
                # 标记相似度
                cv2.putText(quyujieping, f"{i['相似度']}", (int(i["坐标"][0]) + 80, int(i["坐标"][1]) + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 1, cv2.LINE_AA)
                            
        cv2.imshow("video", quyujieping)
        
        # 退出部分
        if cv2.waitKey(5) & 0xFF == ord("q"):
            break
            
finally:
    # 确保资源被正确释放
    camera.stop()
    cv2.destroyAllWindows()