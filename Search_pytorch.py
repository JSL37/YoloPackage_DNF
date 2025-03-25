import mss
import cv2
import numpy as np
from ultralytics import YOLO
import time
import matplotlib.pyplot as plt

# 加载模型
model = YOLO('best.pt')  # 预训练的YOLOv8n模型

# 定义截屏区域
quyu = {"left": 1215, "top": 511, "width": 700, "height": 500}

# 实例化截屏工具
with mss.mss() as sct:
    while True:  # 死循环
        # 获取区域截屏
        quyujieping = sct.grab(quyu)
        quyujieping = np.array(quyujieping)
        quyujieping2 = cv2.cvtColor(quyujieping, cv2.COLOR_BGRA2RGB)

        # 在图片列表上运行设置推理
        # results = model(quyujieping2, stream=True, verbose=False, max_det=100)  # 添加 verbose=False 禁用控制台输出
        results = model(quyujieping2, stream=True, verbose=True)  # 添加 verbose=False 参数

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
                    tuili_jieguo.append({"类别": leibie, "相似度": xiangsidu, "坐标": zuobiao})  # 将信息添加到字典
        # print("推理结果：",tuili_jieguo) #推理结果： [{'类别': '小地图', '相似度': '0.9', '坐标': [565.7940063476562, 59.64765930175781, 656.8956909179688, 108.9930648803711]}, {'类别': '技能框', '相似度': '0.9', '坐标': [18.53238296508789, 174.91871643066406, 193.1510772705078, 223.55274963378906]}, {'类别': '门', '相似度': '0.8', '坐标': [37.60533142089844, 268.97430419921875, 104.484619140625, 336.3001403808594]}, {'类别': '技能框', '相似度': '0.8', '坐标': [263.46539306640625, 452.94940185546875, 437.75311279296875, 500.0]}, {'类别': '称号', '相似度': '0.3', '坐标': [350.1699523925781, 220.61656188964844, 420.4002685546875, 241.98497009277344]}, {'类别': '怪物', '相似度': '0.2', '坐标': [103.3122787475586, 247.00115966796875, 212.85142517089844, 306.6675720214844]}]
        # 画框
        print(tuili_jieguo)
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
            cv2.destroyAllWindows()
            break