
1、引用大漠模块代码
    dm_helper.py
    引用方式
    from dm_helper import get_dm_instance
2、引用KM键鼠操作
    km_controller.py
    引用方式
    from km_controller import KMController
    --------------------------------------------
    import time
    from km_controller import KMController
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
    --------------------------------------------