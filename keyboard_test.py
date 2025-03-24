import random

'''

键盘类api测试

#加密类型
enc_keydown ：按键按下
kmNet.enc_keydown(4)  #保持键盘a键按下
enc_keyup   :按键松开
kmNet.enc_keyup(4)  #松开键盘a键
enc_keypress:单击一次按键
kmNet.enc_keypress(4)  #单击键盘a键

# 鼠标滚轮
# 鼠标滚轮控制, 大于0下移动,小于0上移动
enc_wheel控制鼠标滚轮

# left | enc_left控制鼠标左键
# 鼠标左键控制 isdown :0松开 ，1按下 返回值：0正常执行，其他值异常。

# right | enc_right控制鼠标右键
# 鼠标右键控制 isdown :0松开 ，1按下 返回值：0正常执行，其他值异常。

# middle | enc_middle控制鼠标中键
# 鼠标中键控制 isdown :0松开 ，1按下 返回值：0正常执行，其他值异常。

'''
import kmNet
import time
#连接盒子
ip='192.168.2.188'
port ='1282'
uuid ='AF425414'
kmNet.init(ip,port,uuid)
print('连接盒子ok')



"""
封装二阶贝塞尔曲线移动，自动生成控制点使移动更像人类
鼠标移动
参数:
    target_x: 目标X坐标
    target_y: 目标Y坐标
    duration_ms: 移动耗时(毫秒)
"""
def human_move_bezier(target_x, target_y, duration_ms):
    # 获取当前鼠标位置作为起点
    current_x, current_y = kmNet.get_cursor_position()
    
    # 计算距离
    distance = ((target_x - current_x)**2 + (target_y - current_y)**2)**0.5
    
    # 基于距离和方向添加随机性生成控制点
    # 移动距离越大，控制点偏移量越大，但保持一定比例
    max_offset = min(distance * 0.4, 100)  # 限制最大偏移
    
    # 为控制点1生成随机偏移
    offset_x1 = random.uniform(-max_offset, max_offset)
    offset_y1 = random.uniform(-max_offset, max_offset)
    
    # 为控制点2生成随机偏移，但靠近目标点
    offset_x2 = random.uniform(-max_offset/2, max_offset/2)
    offset_y2 = random.uniform(-max_offset/2, max_offset/2)
    
    # 计算控制点坐标
    # 控制点1位于起点和终点之间的某个位置附近
    control_x1 = current_x + (target_x - current_x) * 0.3 + offset_x1
    control_y1 = current_y + (target_y - current_y) * 0.3 + offset_y1
    
    # 控制点2位于起点和终点之间靠近终点的位置附近
    control_x2 = current_x + (target_x - current_x) * 0.7 + offset_x2
    control_y2 = current_y + (target_y - current_y) * 0.7 + offset_y2
    
    # 调用原始的贝塞尔曲线移动函数
    kmNet.move_beizer(target_x, target_y, duration_ms, 
                      control_x1, control_y1, 
                      control_x2, control_y2)
    return True


"""
封装键盘按键操作函数
"""
# 全局键盘映射表
KEY_MAP = {
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

def get_key_code(key):
    # 如果是数字或字符串形式的数字，直接使用
    if isinstance(key, int) or (isinstance(key, str) and key.isdigit()):
        return int(key)
    else:
        # 转换为小写并查找映射
        key = str(key).lower()
        if key in KEY_MAP:
            return KEY_MAP[key]
        else:
            print(f"未知按键: {key}")
            return None

def keyD(key):
    key_code = get_key_code(key)
    if key_code is not None:
        return kmNet.enc_keydown(key_code)
    return False

def keyU(key):
    key_code = get_key_code(key)
    if key_code is not None:
        return kmNet.enc_keyup(key_code)
    return False

def keyP(key):
    key_code = get_key_code(key)
    if key_code is not None:
        return kmNet.enc_keypress(key_code)
    return False



