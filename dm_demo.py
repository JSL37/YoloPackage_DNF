from dm_helper import get_dm_instance


def main():
    success, dm = get_dm_instance()
    if not success:
        print("大漠注册失败！")
        return

    print(f"大漠版本: {dm.Ver()}")

    hwnd = dm.FindWindowSuper("图片查看", 0, 1, "ImagePreviewWnd", 2, 0)
    if hwnd == 0:
        print("未找到窗口！")
        return
    print(f"绑定窗口句柄: {hwnd}")

    if dm.BindWindowEx(hwnd, "dx.graphic.opengl", "normal", "normal", "", 0) != 1:
        print(f"绑定窗口失败，错误码: {dm.GetLastError()}")
        return

    ai_path = r"E:\7.2450\yolo\ai.module"
    model_path = r"E:\7.2450\yolo\yolov5s_best.dmx"
    pwd = "abc"

    if dm.LoadAi(ai_path) != 1:
        print("AI模块加载失败！")
        return

    print("设置YOLO版本状态:", dm.AiYoloSetVersion("v5-7.0"))
    print("加载模型状态:", dm.AiYoloSetModel(0, model_path, pwd))
    print("激活模型状态:", dm.AiYoloUseModel(0))

    # 获取窗口尺寸
    rect = dm.GetClientRect(hwnd)
    print(f"原始窗口尺寸返回值: {rect}")

    # 直接处理元组或列表
    if isinstance(rect, tuple) or isinstance(rect, list):
        # 如果返回的是一个5元素的序列，第一个是状态码
        if len(rect) == 5:
            status, left, top, right, bottom = rect
            # 检查状态码
            if status != 1:
                print(f"获取窗口尺寸失败，状态码: {status}")
                return
        else:
            print(f"意外的窗口尺寸返回格式: {rect}")
            return
    else:
        print(f"GetClientRect返回了未知类型: {type(rect)}")
        return

    width = right - left
    height = bottom - top
    print(f"窗口客户区尺寸: {width}x{height}")

    # 使用这些尺寸进行检测
    x1, y1 = 0, 0
    x2, y2 = width, height
    prob = 0.3
    iou = 0.4

    print(f"准备检测区域: ({x1},{y1}) - ({x2},{y2})")

    objects = dm.AiYoloDetectObjects(x1, y1, x2, y2, prob, iou)
    print(objects)
    objects = dm.AiYoloSortsObjects(objects, 40)
    print(objects)

    print(dm.AiYoloObjectsToString(objects))
    print(dm.AiYoloDetectObjectsToFile(x1, y1, x2, y2, prob, iou, "test.bmp", 0))
    dm.AiYoloFreeModel(1)


if __name__ == "__main__":
    main()
