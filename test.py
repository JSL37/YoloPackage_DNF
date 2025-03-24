import mss
import cv2
import numpy as np
from ultralytics import YOLO

# 加载模型
model = YOLO('best.pt')  # 预训练的YOLOv8n模型

# 定义截屏区域
quyu = {"left": 35, "top": 216, "width": 697, "height": 340}

# 实例化截屏工具
with mss.mss() as sct:
    while True:  # 死循环
        # 获取区域截屏
        quyujieping = sct.grab(quyu)
        quyujieping = np.array(quyujieping)
        quyujieping2 = cv2.cvtColor(quyujieping, cv2.COLOR_BGRA2RGB)

        # 在图片列表上运行设置推理
        results = model(quyujieping2, stream=True)  # 返回Results对象生成器

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

        # 画框
        # print(tuili_jieguo)
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

        # 显示窗口部分
        # cv2.namedWindow("game", cv2.WINDOW_NORMAL)  # 窗口等比缩放
        # cv2.resizeWindow("game", quyu['width'] // 2, quyu['height'] // 2)  # 用于裁剪显示窗口
        cv2.imshow("video", quyujieping)

        # 退出部分
        if cv2.waitKey(5) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
