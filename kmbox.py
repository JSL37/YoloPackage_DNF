import kmNet
import time
ip='192.168.2.177'
port ='1101'
uuid ='96C07019'
a = kmNet.init(ip,port,uuid)
while True:
    kmNet.enc_right(1)#鼠标右键按下
    kmNet.enc_right(0)#鼠标右键松开
    
    time.sleep(1)
    kmNet.keydown (8)
    kmNet.keyup(8)
    
    time.sleep(1)






