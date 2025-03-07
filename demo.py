# 在你的主程序文件中

# 导入便捷函数
from dm_helper import get_dm_instance
# 使用示例
from km_controller import KMController

# 初始化控制器
ip = '192.168.2.177'
port = '1101'
uuid = '96C07019'
km = KMController(ip, port, uuid)

# 模拟右键点击
km.mouse_right_click()
time.sleep(1)

# 模拟按下E键
km.press_key(km.KEY_E)
time.sleep(1)

# 输入一段文本
km.type_string("Hello World")

# 组合键示例：Ctrl+C
km.key_down(km.KEY_CTRL_L)
km.press_key(km.KEY_C)
km.key_up(km.KEY_CTRL_L)


# 获取注册状态和大漠对象
success, dm = get_dm_instance()

# 根据返回状态决定是否输出信息
if success:
    print("大漠注册成功!")
    print("大漠版本: {}".format(dm.Ver()))

    # 正常使用大漠对象
    dm.MoveTo(123, 123)

    # 继续你的其他操作...
else:
    print("注册失败，请检查注册码或DLL文件!")