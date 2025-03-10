# 导入便捷函数
from dm_helper import get_dm_instance

# 获取注册状态和大漠对象
success, dm = get_dm_instance()

# 根据返回状态决定是否输出信息
if success:
    print("大漠注册成功!")
    print("大漠版本: {}".format(dm.Ver()))

    # 正常使用大漠对象
    dm.MoveTo(123, 123)

else:
    print("注册失败，请检查注册码或DLL文件!")