#! /usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import win32com.client
import os
import base64


class DMHelper:
    def __init__(self):
        self.dm = None

    def initialize(self):
        """初始化并注册大漠对象，返回注册结果和大漠对象"""
        # Get the current script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Use paths relative to the script location
        dm_reg_path = os.path.join(current_dir, "DmReg.dll")
        dm_dll_path = os.path.join(current_dir, "dm.dll")

        # 免注册调用
        obj = ctypes.windll.LoadLibrary(dm_reg_path)
        obj.SetDllPathW(dm_dll_path, 0)

        # 创建大漠对象
        self.dm = win32com.client.DispatchEx("dm.dmsoft")

        # 注册大漠
        reg_code, ver_code = self._decode_reg_code()
        res = self.dm.Reg(reg_code, ver_code)

        return res, self.dm

    def _decode_reg_code(self):
        """解码注册码"""
        # Encoded registration code
        encoded_reg_code = "anY5NjU3MjBiMjM5YjgzOTZiMWI3ZGY4Yjc2OGM5MTllODZlMTBm"
        encoded_ver_code = "ajBwdjZjazJkY2x2N2cyNw=="

        # Decode the registration codes
        reg_code = base64.b64decode(encoded_reg_code).decode('utf-8')
        ver_code = base64.b64decode(encoded_ver_code).decode('utf-8')

        return reg_code, ver_code


# 便捷函数，可以直接导入
def get_dm_instance():
    """获取已初始化和注册的大漠对象

    Returns:
        tuple: (success, dm)
            - success (bool): 注册是否成功 (1为成功)
            - dm: 大漠对象实例
    """
    helper = DMHelper()
    res, dm = helper.initialize()
    # 将注册结果转换为布尔值
    success = res == 1
    return success, dm
