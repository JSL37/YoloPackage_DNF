import mss
import cv2
import numpy as np
from ultralytics import YOLO
import time
import tkinter as tk
from PIL import Image, ImageTk

# 加载模型
model = YOLO('best.pt')  # 预训练的YOLOv8n模型

# 定义截屏区域
quyu = {"left": 1163, "top": 129, "width": 1280, "height": 720}

# 创建主窗口
root = tk.Tk()
root.title("实时检测")

# 图像展示区域
image_label = tk.Label(root)
image_label.pack(side=tk.LEFT, padx=10, pady=10)

# 检测结果显示区域
detection_text = tk.Text(root, height=20, width=40)
detection_text.pack(side=tk.LEFT, padx=10, pady=10)

# 状态显示区域
status_text = tk.Text(root, height=20, width=40)
status_text.pack(side=tk.RIGHT, padx=10, pady=10)

def update_image_and_results():
    with mss.mss() as sct:
        quyujieping = sct.grab(quyu)
        quyujieping = np.array(quyujieping)
        quyujieping2 = cv2.cvtColor(quyujieping, cv2.COLOR_BGRA2RGB)

        results = model(quyujieping2, stream=True, verbose=False)

        tuili_jieguo = []

        for result in results:
            if len(result.boxes.cls) > 0:
                for i in range(len(result.boxes.cls)):
                    leibie_id = int(result.boxes.cls[i].item())
                    leibie = result.names[leibie_id]
                    xiangsidu = str(result.boxes.conf[i].item())[0:3]
                    zuobiao = result.boxes.xyxy[i].tolist()
                    tuili_jieguo.append({"类别": leibie, "相似度": xiangsidu, "坐标": zuobiao})

        if len(tuili_jieguo) > 0:
            detection_text.delete(1.0, tk.END)
            for i in tuili_jieguo:
                detection_text.insert(tk.END, f"类别: {i['类别']}, 相似度: {i['相似度']}, 坐标: {i['坐标']}\n")
                cv2.rectangle(quyujieping, (int(i["坐标"][0]), int(i["坐标"][1])), (int(i["坐标"][2]), int(i["坐标"][3])),
                              (0, 255, 0), 2)
                cv2.putText(quyujieping, f"{i['类别']}", (int(i["坐标"][0]), int(i["坐标"][1]) + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(quyujieping, f"{i['相似度']}", (int(i["坐标"][0]) + 80, int(i["坐标"][1]) + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

        img = Image.fromarray(cv2.cvtColor(quyujieping, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(image=img)
        image_label.img_tk = img_tk
        image_label.configure(image=img_tk)

    root.after(50, update_image_and_results)  # 每50毫秒更新一次

def on_closing():
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

update_image_and_results()
root.mainloop()