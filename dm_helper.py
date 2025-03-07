#! /usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import ctypes
import os

import win32com.client


class DMHelper:
    def __init__(self):
        self.dm = None

    def initialize(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dm_reg_path = os.path.join(current_dir, "DmReg.dll")
        dm_dll_path = os.path.join(current_dir, "dm.dll")
        obj = ctypes.windll.LoadLibrary(dm_reg_path)
        obj.SetDllPathW(dm_dll_path, 0)
        self.dm = win32com.client.DispatchEx("dm.dmsoft")
        reg_code, ver_code = self._decode_reg_code()
        res = self.dm.Reg(reg_code, ver_code)

        return res, self.dm

    def _decode_reg_code(self):
        encoded_reg_code = "anY5NjU3MjBiMjM5YjgzOTZiMWI3ZGY4Yjc2OGM5MTllODZlMTBm"
        encoded_ver_code = "ajBwdjZjazJkY2x2N2cyNw=="

        # Decode the registration codes
        reg_code = base64.b64decode(encoded_reg_code).decode('utf-8')
        ver_code = base64.b64decode(encoded_ver_code).decode('utf-8')

        return reg_code, ver_code


def get_dm_instance():
    helper = DMHelper()
    res, dm = helper.initialize()
    # 将注册结果转换为布尔值
    success = res == 1
    return success, dm
