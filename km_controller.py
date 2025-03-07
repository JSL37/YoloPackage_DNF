import kmNet
import time


class KMController:
    # 键盘按键常量
    # 字母键
    KEY_A = 4
    KEY_B = 5
    KEY_C = 6
    KEY_D = 7
    KEY_E = 8
    KEY_F = 9
    KEY_G = 10
    KEY_I = 12
    KEY_J = 13
    KEY_K = 14
    KEY_M = 18
    KEY_N = 15
    KEY_O = 20
    KEY_Q = 23
    KEY_R = 19
    KEY_S = 22
    KEY_T = 25
    KEY_U = 21
    KEY_V = 28
    KEY_W = 26
    KEY_X = 27
    KEY_Y = 43
    KEY_Z = 29

    # 数字键
    KEY_0 = 39
    KEY_2 = 31
    KEY_3 = 30
    KEY_4 = 33
    KEY_5 = 32
    KEY_6 = 35
    KEY_7 = 34
    KEY_9 = 36

    # 特殊键
    KEY_SPACE = 44
    KEY_TAB = 44
    KEY_ENTER = 40
    KEY_ESC = 41
    KEY_BACKSPACE = 42
    KEY_DELETE = 76
    KEY_SHIFT = 37
    KEY_SHIFT_L = 225
    KEY_SHIFT_R = 229
    KEY_CTRL_L = 224
    KEY_CTRL_R = 228
    KEY_ALT_L = 226
    KEY_ALT_R = 230
    KEY_GUI_L = 227
    KEY_GUI_R = 231
    KEY_CAPS = 57

    # 方向键
    KEY_UP = 82
    KEY_DOWN = 81
    KEY_LEFT = 80
    KEY_RIGHT = 79

    # 功能键
    KEY_F1 = 58
    KEY_F2 = 59
    KEY_F3 = 60
    KEY_F4 = 61
    KEY_F5 = 62
    KEY_F6 = 63
    KEY_F7 = 64
    KEY_F8 = 65
    KEY_F9 = 66
    KEY_F10 = 67
    KEY_F11 = 68
    KEY_F12 = 69
    KEY_F13 = 104
    KEY_F14 = 105
    KEY_F15 = 106
    KEY_F16 = 107
    KEY_F17 = 108
    KEY_F18 = 109
    KEY_F19 = 110
    KEY_F20 = 111

    # 其他特殊键
    KEY_HOME = 74
    KEY_END = 77
    KEY_INSERT = 73
    KEY_PGUP = 71
    KEY_PGDOWN = 78
    KEY_PRINT = 55
    KEY_SCROLL = 56
    KEY_PAUSE = 70
    KEY_HELP = 254
    KEY_BRACKET_LEFT = 49
    KEY_BRACKET_RIGHT = 48
    KEY_SLASH = 54
    KEY_DOT = 53
    KEY_APLC = 101

    def __init__(self, ip, port, uuid):
        """初始化键鼠控制器

        Args:
            ip (str): 设备IP地址
            port (str): 端口号
            uuid (str): 设备UUID
        """
        self.controller = kmNet.init(ip, port, uuid)

    def press_key(self, key_code, duration=0.1):
        """按下并释放按键

        Args:
            key_code (int): 按键码
            duration (float, optional): 按下持续时间(秒). 默认0.1秒.
        """
        kmNet.keydown(key_code)
        time.sleep(duration)
        kmNet.keyup(key_code)

    def key_down(self, key_code):
        """按下按键

        Args:
            key_code (int): 按键码
        """
        kmNet.keydown(key_code)

    def key_up(self, key_code):
        """释放按键

        Args:
            key_code (int): 按键码
        """
        kmNet.keyup(key_code)

    def mouse_left_click(self, duration=0.1):
        """左键点击

        Args:
            duration (float, optional): 点击持续时间(秒). 默认0.1秒.
        """
        kmNet.enc_left(1)
        time.sleep(duration)
        kmNet.enc_left(0)

    def mouse_right_click(self, duration=0.1):
        """右键点击

        Args:
            duration (float, optional): 点击持续时间(秒). 默认0.1秒.
        """
        kmNet.enc_right(1)
        time.sleep(duration)
        kmNet.enc_right(0)

    def mouse_left_down(self):
        """按下鼠标左键"""
        kmNet.enc_left(1)

    def mouse_left_up(self):
        """释放鼠标左键"""
        kmNet.enc_left(0)

    def mouse_right_down(self):
        """按下鼠标右键"""
        kmNet.enc_right(1)

    def mouse_right_up(self):
        """释放鼠标右键"""
        kmNet.enc_right(0)

    def mouse_move(self, x, y):
        """移动鼠标到指定位置

        Args:
            x (int): X坐标
            y (int): Y坐标
        """
        kmNet.enc_pos(x, y)

    def mouse_move_rel(self, dx, dy):
        """移动鼠标（相对位置）

        Args:
            dx (int): X方向移动距离
            dy (int): Y方向移动距离
        """
        kmNet.enc_rel(dx, dy)

    def type_string(self, text, delay=0.05):
        """输入字符串

        Args:
            text (str): 要输入的文本
            delay (float, optional): 按键间延迟(秒). 默认0.05秒.
        """
        key_map = {
            'a': self.KEY_A, 'b': self.KEY_B, 'c': self.KEY_C, 'd': self.KEY_D,
            'e': self.KEY_E, 'f': self.KEY_F, 'g': self.KEY_G, 'i': self.KEY_I,
            'j': self.KEY_J, 'k': self.KEY_K, 'm': self.KEY_M, 'n': self.KEY_N,
            'o': self.KEY_O, 'q': self.KEY_Q, 'r': self.KEY_R, 's': self.KEY_S,
            't': self.KEY_T, 'u': self.KEY_U, 'v': self.KEY_V, 'w': self.KEY_W,
            'x': self.KEY_X, 'y': self.KEY_Y, 'z': self.KEY_Z,
            '0': self.KEY_0, '2': self.KEY_2, '3': self.KEY_3, '4': self.KEY_4,
            '5': self.KEY_5, '6': self.KEY_6, '7': self.KEY_7, '9': self.KEY_9,
            ' ': self.KEY_SPACE, '.': self.KEY_DOT, '/': self.KEY_SLASH,
            '[': self.KEY_BRACKET_LEFT, ']': self.KEY_BRACKET_RIGHT
        }

        for char in text:
            if char.lower() in key_map:
                if char.isupper():
                    self.key_down(self.KEY_SHIFT)
                    self.press_key(key_map[char.lower()])
                    self.key_up(self.KEY_SHIFT)
                else:
                    self.press_key(key_map[char.lower()])
                time.sleep(delay)