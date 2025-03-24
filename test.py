# test_script.py

import keyboard as k
import kmNet
import time

# 连接盒子
ip = '192.168.2.177'
port = '1101'
uuid = '96C07019'
kmNet.init(ip, port, uuid)
print('连接盒子ok')

k.find_procedure()

k.walk_down()
time.sleep(2)
k.cancel_direction("down")
k.walk_left()
time.sleep(5)
k.cancel_direction("left")

# kmNet.enc_keydown(81)
# time.sleep(5)
# kmNet.enc_keyup(81)
