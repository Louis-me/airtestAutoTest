#!/usr/bin/env python
# -*- coding=utf-8 -*-
import threading
from airtest.core.api import *
from util.read_ini1 import ReadIni
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from airtest.core.android.android import *
from util.log_util import log as ut_log
from selenium_driver import Element

def attached_devices():
    command_result = ''
    command_text = 'adb devices'
    results = os.popen(command_text, "r")
    while 1:
        line = results.readline()
        if not line: break
        command_result += line
    results.close()
    devices = command_result.partition('\n')[2].replace('\n', '').split('\tdevice')
    return [device for device in devices if len(device) > 2]


def install_apk_(apk):
    install(apk, install_options=["-r", "-t", "-g"])


def init_android(data):
    print("-----设备名称----")
    print(data["device"])
    if data["save_image"] == "1":
        ST.SAVE_IMAGE = True
        ut_log.info("由于设置了save_image为1,测试步骤需要截图")
    else:
        ST.SAVE_IMAGE = False
        ut_log.info("由于设置了save_image为0,测试步骤不需要截图")
    try:
        # 注意这里初始化设备需要正确
        auto_setup(__file__, devices=data["device"])
        poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

        Element.poco = poco
        # Element.poco1.put(poco)
        print("初始化")
        print(Element.poco)
    except Exception as e:
        ut_log.error("初始化设备异常,请检查=", data["device"])
        return
    android_ini = ReadIni.get_android()
    apk = android_ini.get("apk")
    pkg = android_ini.get("pkg")
    if data["install_type"] == "2":
        ut_log.info("%s卸载并重装应用:%s" % (data["dev"], pkg))
        un_install(pkg, apk)
    elif data["install_type"] == "1":
        ut_log.info("%s直接覆盖安装应用:%s" % (data["dev"], pkg))
        # update_install(apk)
    else:
        print("应用不做任何处理")
    time.sleep(5)
    print("--准备打开app----" + pkg)
    start_app(pkg)
    print("--app打开成功----")


def check_login():
    """
    检查登录
    在使用时可能没有登录，进行登录操作

    :return:
    """

    # 这里可以做个检查点，打开应用时若没有进行登录，那么就可以进行的管理操作
    pass

    # 点击允许
    # poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
    poco = Element.poco
    if poco("com.android.systemui:id/notification_allow").wait(2).exists():
        poco("com.android.systemui:id/notification_allow").click()
        # 后续是启动后对应用进行登录操作
        # 点击同意
    poco("com.jianshu.haruki:id/tv_ok").wait(15).click()
    # 点击切换登录方式
    if poco("com.jianshu.haruki:id/tv_switch_login_mode").wait(3).exists():
        poco("com.jianshu.haruki:id/tv_switch_login_mode").click()
    if poco("com.jianshu.haruki:id/gt_one_login_switch_tv").wait(3).exists():
        poco("com.jianshu.haruki:id/gt_one_login_switch_tv").click()
    # 输入用户名和密码
    poco("com.jianshu.haruki:id/et_account").set_text("18576759588")
    poco("com.jianshu.haruki:id/et_verification_code_or_password").wait(1).set_text("11234555")
    poco("com.jianshu.haruki:id/tv_user_cb").wait(1).click()
    poco("com.jianshu.haruki:id/tv_login").click()


def un_install(pkg, apk):
    """
    卸载并重新安装应用，并且自动登录
    :return:
    """
    try:
        uninstall(pkg)
    except Exception as e:
        pass
    # 安装app
    threading.Thread(target=install_apk_, args=(), kwargs={"apk": apk}).start()
    time.sleep(3)
    print("------------")
    # 安装app出现的提示
    num = 5
    while num > 0:
        time.sleep(1)
        print("等待点击继续安装")
        try:
            ST.CVSTRATEGY = ["tpl", "mstpl", "sift", "brisk"]

            if exists(Template(r"tpl1694398259508.png", threshold=0.7, record_pos=(-0.027, 0.971),
                               resolution=(1080, 2408))):
                touch(Template(r"tpl1694398259508.png", threshold=0.7, record_pos=(-0.027, 0.971),
                               resolution=(1080, 2408)))
                num = 0
                print("点击继续安装成功")
        except Exception as e:
            pass
        num -= 1
    check_login()


def update_install(apk):
    """
    直接覆盖安装
    :return:
    """
    threading.Thread(target=install_apk_, args=(), kwargs={"apk": apk}).start()
    time.sleep(3)
    print("----覆盖安装成功--------")
    # 安装app出现的提示
    num = 5
    while num > 0:
        time.sleep(1)
        print("等待点击继续安装")
        try:
            ST.CVSTRATEGY = ["tpl", "mstpl", "sift", "brisk"]

            if exists(Template(r"tpl1694398259508.png", threshold=0.7, record_pos=(-0.027, 0.971),
                               resolution=(1080, 2408))):
                touch(Template(r"tpl1694398259508.png", threshold=0.7, record_pos=(-0.027, 0.971),
                               resolution=(1080, 2408)))
                num = 0
                print("点击继续安装成功")
        except Exception as e:
            pass
        num -= 1
