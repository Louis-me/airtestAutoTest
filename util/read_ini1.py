# -*- coding: utf-8 -*-
import configparser
import os
import json

from util.log_util import log as ut_log
"""
读取ini文件
"""

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class ReadIni(object):

    @classmethod
    def get_setting(cls):
        setting_path = PATH("../config/setting.ini")
        if not os.path.exists(setting_path):
            ut_log.error("请检查配置文件是否存在:%s" % setting_path)
            return
        cls.config = configparser.ConfigParser()
        cls.config.read(setting_path, encoding='utf-8')
        platform = cls.config['default']['platform']
        mail_enable = True if cls.config['default']['mail_enable'] == 'true' else False
        report_host = cls.config['default']['report_host']
        local_host_port = cls.config['default']['local_host_port']
        local_host_path = cls.config['default']['local_host_path']
        remove_log = True if cls.config['default']['remove_log'] == 'true' else False
        recording = True if cls.config['default']['recording'] == 'true' else False
        save_image = cls.config['default']['save_image']

        return {"platform": platform, "mail_enable": mail_enable, "report_host": report_host,"local_host_path": local_host_path,
                "local_host_port": local_host_port, "remove_log": remove_log, "recording": recording, "save_image": save_image}

    @classmethod
    def get_platform(cls, plat):
        if plat == "android":
            return cls().get_android()
        elif plat == "ios":
            return cls().get_ios()
        elif plat == "web":
            return cls().get_web()
        else:
            print("请输入正确的平台")
            return {"result": False}

    @classmethod
    def get_android(cls):
        path1 = PATH("../config/android.ini")
        if not os.path.exists(path1):
            ut_log.error("请检查配置文件android.ini是否存在:%s" % path1)
            return {"result": False}
        cls.config = configparser.ConfigParser()
        cls.config.read(path1, encoding='utf-8')
        pkg = cls.config['default']['pkg']
        phone = cls.config['default']['phone']
        dev_connect = cls.config['default']['dev_connect']
        dev = cls.config['default']['dev']
        root_path = cls.config['default']['root_path']
        test_plan = int(cls.config['default']['test_plan'])
        test_module = json.loads(cls.config['default']['test_module'])
        boot = cls.config['default']['boot']
        apk = cls.config['default']['apk']
        install_type = cls.config['default']['install_type']
        test_case = cls.config["multi"].get("test_case", "[]")
        if test_case:
            multi_test_case = json.loads(test_case)
            for i in range(len(multi_test_case)):
                multi_test_case[i]["plat"] = "android"
        else:
            multi_test_case = []

        data = {"pkg": pkg, "phone": phone, "dev_connect": dev_connect, "dev": dev,"apk": apk, "install_type": install_type,
                "root_path": root_path, "test_plan": test_plan, "test_module": test_module, "boot": boot, "test_case": multi_test_case}

        return data

    @classmethod
    def get_web(cls):
        path1 = PATH("../config/web.ini")
        if not os.path.exists(path1):
            ut_log.error("请检查配置文件web.ini是否存在:%s" % path1)
            return {"result": False}

        cls.config = configparser.ConfigParser()
        cls.config.read(path1, encoding='utf-8')

        dev = cls.config['default']['dev']
        phone = cls.config['default']['phone']
        chrome_driver = cls.config['default']['chrome_driver']
        chrome_exe = cls.config['default']['chrome_exe']
        login_url = cls.config['default']['login_url']
        # home_url = cls.config['default']['home_url']
        boot = cls.config['default']['boot']
        root_path = cls.config['default']['root_path']
        test_plan = int(cls.config['default']['test_plan'])
        test_module = json.loads(cls.config['default']['test_module'])
        test_case = cls.config["multi"].get("test_case", "[]")
        if test_case:
            multi_test_case = json.loads(test_case)
            for i in range(len(multi_test_case)):
                multi_test_case[i]["plat"] = "android"
        else:
            multi_test_case = []

        data = {"chrome_driver": chrome_driver, "chrome_exe": chrome_exe, "login_url": login_url, "boot": boot,"phone":phone,
                "test_case": multi_test_case, "root_path": root_path, "test_plan": test_plan, "test_module": test_module,
                "dev": dev}
        return data

    @classmethod
    def get_ios(cls):
        pass


if __name__ == "__main__":
    s = ReadIni().get_setting()
    print(s)
    # print(type(s))
# t = ReadIni(Br('conf.ini')).get_host()
