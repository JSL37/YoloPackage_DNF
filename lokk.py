from ultralytics import YOLO

# 加载模型
model = YOLO('best.pt')  # 你的YOLOv8模型路径

# 导出为ONNX格式
model.export(format='onnx', dynamic=True, simplify=True)