# -*- coding=utf-8 -*-
from util.read_ini1 import ReadIni
from multi_runner import multi_runner
from single_runner import single_runner

if __name__ == "__main__":

    setting_ini_data = ReadIni().get_setting()
    if not setting_ini_data.get("result", "1"):
        print("请确认setting.ini文件是否配置正确")

    else:
        plat = setting_ini_data["platform"]
        plat_ini_data = ReadIni.get_platform(plat)
        setting_ini_data.update(plat_ini_data)
        if not plat_ini_data.get("result", "1"):
            print("请确认%s.ini文件是否配置正确" % plat)
        else:
            if plat_ini_data.get("boot") == "multi":
                print("多机启动器启动")
                multi_runner(setting_ini_data)
            else:
                print("单机启动器启动")
                single_runner(setting_ini_data)