import random
import kmNet
import time
import math


"""
封装键盘按键操作函数
"""
# 全局键盘映射表
KEY_MAP = {  # 用户提供的键盘映射表（保持原样）
    'space': 44, 'a': 4, 'd': 7, 'g': 10, '4': 33, '5': 34, '6': 35, '7': 36, '8': 37, '9': 38, '0': 39,
    '-': 45, '=': 46, 'q': 20, 'w': 26, 'e': 8, 'r': 21, 't': 23, 'y': 28, 'u': 24, 'i': 12, 'o': 18,
    'p': 19, '[': 47, ']': 48, '\\': 49, 'caps': 57, 's': 22, 'f': 9, 'h': 11, 'j': 13, 'k': 14, 'l': 15,
    ';': 51, "'": 52, 'enter': 40, 'shift': 225, 'z': 29, 'x': 27, 'c': 6, 'v': 25, 'b': 5, 'n': 17,
    'm': 16, ',': 54, '.': 55, '/': 56, 'ctrl': 224, 'alt': 226, 'tab': 43, 'esc': 41, 'f1': 58, 'f2': 59,
    'f3': 60, 'f4': 61, 'f5': 62, 'f6': 63, 'f7': 64, 'f8': 65, 'f9': 66, 'f10': 67, 'f11': 68, 'f12': 69,
    'print': 70, 'scroll': 71, 'pause': 72, 'insert': 73, 'home': 74, 'pageup': 75, 'delete': 76, 'end': 77,
    'pagedown': 78, 'right': 79, 'left': 80, 'down': 81, 'up': 82, 'num_lock': 83, 'ctrl-l': 224, 'ctrl-r': 228,
    'shift-l': 225, 'shift-r': 229, 'alt-l': 226, 'alt-r': 230, 'gui-l': 227, 'gui-r': 231, 'help': 254,
    'f13': 104, 'f14': 105, 'f15': 106, 'f16': 107, 'f17': 108, 'f18': 109, 'f19': 110, 'aplcat': 101
}

def KD(key_name):
    """按下指定键"""
    code = KEY_MAP.get(key_name.lower(), None)  # 转小写处理，支持大小写不敏感
    if code is None:
        raise ValueError(f"未找到键 '{key_name}' 的映射，请检查键名是否正确！")
    kmNet.keydown(code)

def KU(key_name):
    """释放指定键"""
    code = KEY_MAP.get(key_name.lower(), None)
    if code is None:
        raise ValueError(f"未找到键 '{key_name}' 的映射，请检查键名是否正确！")
    kmNet.keyup(code)

def KC(key_name):
    """点击指定键（按下后立即释放）"""
    code = KEY_MAP.get(key_name.lower(), None)
    if code is None:
        raise ValueError(f"未找到键 '{key_name}' 的映射，请检查键名是否正确！")
    kmNet.keydown(code)
    kmNet.keyup(code)

def run_z():
    """左奔跑"""
    # 快速两次按左键触发奔跑
    KC('left')
    time.sleep(0.1)
    KD('left')

def run_y():
    """右奔跑"""
    # 快速两次按右键触发奔跑
    KC('right')
    time.sleep(0.1)
    KD('right')

def run_zs():
    """左上奔跑"""
    # 先触发左奔跑，再同时按左和上键
    run_z()
    KD('up')

def run_zx():
    """左下奔跑"""
    run_z()
    KD('down')

def run_ys():
    """右上奔跑"""
    run_y()
    KD('up')

def run_yx():
    """右下奔跑"""
    run_y()
    KD('down')

# 方向键名列表（用于验证）
DIRECTIONS = ['up', 'down', 'left', 'right']

def walk_up():
    """向前走（按住上方向键）"""
    KD('up')

def walk_down():
    """向后走（按住下方向键）"""
    print("向后走（按住下方向键）")
    KD('down')

def walk_left():
    """向左走（按住左方向键）"""
    print("向左走（按住左方向键）")
    KD('left')

def walk_right():
    """向右走（按住右方向键）"""
    KD('right')

def cancel_direction(direction):
    """取消指定方向按键（参数为方向名称字符串）"""
    direction = direction.lower()
    if direction not in DIRECTIONS:
        raise ValueError(f"无效的方向 '{direction}'，有效方向为：{DIRECTIONS}")
    KU(direction)

def stop_moving():
    """停止所有移动（释放所有方向键）"""
    for key in DIRECTIONS:
        KU(key)

def find_procedure():
    """将页面设为激活状态"""
    # 'ctrl': 224, 'alt': 226,
    KD('alt')
    KD('ctrl')
    time.sleep(0.5)
    KU('alt')
    KU('ctrl')