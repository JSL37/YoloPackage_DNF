import mss
import cv2
import torch
import numpy as np
import onnxruntime as ort
from ultralytics.utils.ops import non_max_suppression

# 模型参数配置
class_names = {
    0: '称号', 1: '小地图', 2: '门', 3: '疲劳', 4: '怪物', 5: '技能框', 6: '材料',
    7: '小地图_角色', 8: '小地图_可移动房间', 9: '小地图_BOSS', 10: '小地图_特殊房间',
    11: '金币', 12: '门_关闭', 13: '协调结晶体', 14: '炉岩核', 15: '妖气残痕', 16: '灵界之石'
}

# 高性能ONNX推理器
class ONNXInferencer:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.io_binding = self.session.io_binding()
        
    def preprocess(self, img):
        """GPU加速的预处理流水线"""
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 640), interpolation=cv2.INTER_LINEAR)
        img = np.ascontiguousarray(img.transpose(2, 0, 1), dtype=np.float32) / 255.0
        return np.expand_dims(img, axis=0)
    
    def infer(self, img):
        """绑定IO的异步推理"""
        input_tensor = self.preprocess(img)
        self.io_binding.bind_input(
            name=self.input_name,
            device_type='cuda',
            device_id=0,
            element_type=np.float32,
            shape=input_tensor.shape,
            buffer_ptr=input_tensor.ctypes.data
        )
        self.io_binding.bind_output(self.session.get_outputs()[0].name, 'cuda')
        self.session.run_with_iobinding(self.io_binding)
        return self.io_binding.copy_outputs_to_cpu()

# 坐标转换工具类
class CoordinateTransformer:
    def __init__(self, capture_area, model_input_size=(640, 640)):
        self.offset_x = capture_area["left"]
        self.offset_y = capture_area["top"]
        self.scale_x = capture_area["width"] / model_input_size[0]
        self.scale_y = capture_area["height"] / model_input_size[1]
    
    def transform(self, x1, y1, x2, y2):
        """模型输出坐标→屏幕绝对坐标"""
        return (
            int(x1 * self.scale_x) + self.offset_x,
            int(y1 * self.scale_y) + self.offset_y,
            int(x2 * self.scale_x) + self.offset_x,
            int(y2 * self.scale_y) + self.offset_y
        )

# 主检测流程
def main():
    # 初始化组件
    detector = ONNXInferencer('best.onnx')
    transformer = CoordinateTransformer(
        capture_area={"left": 1215, "top": 511, "width": 640, "height": 640}
    )
    
    with mss.mss() as sct:
        while True:
            # 屏幕捕获
            frame = np.array(sct.grab(transformer.__dict__))[:, :, :3]
            display_frame = frame.copy()
            
            # 推理流水线
            outputs = detector.infer(frame)
            predictions = torch.from_numpy(outputs[0])
            
            # 后处理
            nms_results = non_max_suppression(
                predictions,
                conf_thres=0.25,
                iou_thres=0.45,
                agnostic=False,
                max_det=300,
                nc=len(class_names)
            )
            
            # 结果解析
            detections = []
            if nms_results[0] is not None:
                for det in nms_results[0]:
                    x1, y1, x2, y2 = transformer.transform(*det[:4])
                    detections.append({
                        'class': class_names[int(det[5])],
                        'confidence': f"{det[4]:.2f}",
                        'bbox': (x1, y1, x2, y2)
                    })
                    
                    # 抗锯齿绘制
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0,255,0), 2, cv2.LINE_AA)
                    label = f"{detections[-1]['class']} {detections[-1]['confidence']}"
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                    cv2.rectangle(display_frame, (x1, y1-20), (x1+tw, y1), (0,0,0), -1)
                    cv2.putText(display_frame, label, (x1, y1-5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)
            
            # 显示输出
            cv2.imshow('DNF Object Detection', display_frame)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
