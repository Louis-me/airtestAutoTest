#!/usr/bin/env python
# -*- coding=utf-8 -*-
import datetime

__CreateAt__ = '2020/4/19-17:34'

import threading

from multiprocessing import Pool

from airtest.cli.runner import AirtestCase, run_script
from argparse import *
import airtest.report.report as report
import jinja2
import shutil
import os
import io

from selenium_driver import Element
from util.log_util import log as ut_log
from util.http_server import HttpServer
from util.android_util import attached_devices, init_android
from util.common import get_case_total_time, MulCommon
from datetime import datetime
import time

from web_util import get_driver

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


def run_case(data):
    """

    :param data:  来源与各ini文件
    :return:
    """
    dev_connect = None
    # 当平台为安卓时，检查是否连接成功
    if data.get("platform", "1") == "android":
        ut_log.debug("启动安卓启动器")
        devices = attached_devices()
        if not devices:
            ut_log.error("无可用设备")
            return
        # Android://127.0.0.1:5037/emulator-5554
        # 设置安卓的连接字符串
        dev_connect = data["dev_connect"]
        # 设备的列表
        data["dev_list"] = devices
    elif data.get("platform", "1") == "ios":
        pass
    elif data.get("platform", "1") == "web":
        ut_log.debug("启动web启动器")

    test = CustomAirtestCase(data["root_path"], dev_connect)
    test.run_air(data)


def run(root_dir, test_case, device, dev_connect, local_host_path, log_date, recording, report_host, phone):
    """

    :param root_dir: 用例目录
    :param test_case:  dict|{"case": "111.air", "module": "小回归"}
    :param device: emulator-5554 如果传web那么就没有这样的连接字符串[dev_connect + device]
    :param dev_connect: Android://127.0.0.1:5037/
    :param local_host_path:  服务器报告目录,这里是aritest的report的目录
    :param log_date:   报告的跟目录 /log/201201201201
    :param recording: 是否录屏 true|false
    :param report_host:   服务器信的信息，比如本地的ip
    :param phone: 设备名称
    :return:
    """
    if device == "web":
        air_device = None
    else:
        air_device = [dev_connect + device]  # 取设备
    script = os.path.join(root_dir, test_case["module"], test_case["case"])
    log_host_path = os.path.join(test_case["module"], test_case["case"].replace('.air', ''))
    log = os.path.join(local_host_path, log_host_path)
    os.makedirs(log, exist_ok=True)
    print(str(log) + ' 创建日志文件成功')
    output_file = os.path.join(log, 'log.html')
    # 用例开始执行日期
    st_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 用例开始执行时间
    s_time = datetime.now().strftime("%H:%M:%S")
    try:
        args = Namespace(device=air_device, log=log, compress=None, recording=recording, script=script, no_image=None)
        t = run_script(args, AirtestCase)
        print("runtest")
        print(t)
        is_success = True
    except Exception as e:
        is_success = False
    end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 用例结束执行时间
    e_time = datetime.now().strftime("%H:%M:%S")
    # 用例耗时时间
    sum_time = get_case_total_time(s_time, e_time)
    # 生成测试用例的详情报告
    rpt = report.LogToHtml(script_root=script, log_root=log, static_root=report_host)
    # rpt = report.LogToHtml(script_root=script, log_root=log, static_root=report_host, plugins=['airtest_selenium.report'])

    rpt.report("log_template.html", output_file=output_file)
    # 记录测试结果
    s_name = test_case["case"].replace(".air", "")
    s_log = os.path.join(report_host, "log", log_date, test_case["module"], s_name)
    result = {"result": is_success, "start_date": st_date, "end_date": end_date, "sum_time": sum_time,
              "log": s_log, "name": s_name, "phone": phone, "dev": device}

    MulCommon.set_result_json(result)

    if not is_success:
        ut_log.error("存在失败用例:%s" % test_case)


class CustomAirtestCase(AirtestCase):
    # @classmethod
    # def setUpClass(cls):
    #     super(CustomAirtestCase,cls).setUpClass()

    def __init__(self, root_path, dev_connect):
        self.fail_data = []
        self.root_path = root_path  # 用例目录
        self.dev_connect = dev_connect  # 设备连接 如：Android://127.0.0.1:5037/
        self.log_date = ""  # 报告的跟目录 /log/201201201201
        self.local_host_path = ""  # 服务器报告目录,这里是aritest的report的目录
        self.recording = ""  # 是否录屏
        self.report_host = ""  # 服务器远程地址，如http://172.31.105.196:8000
        self.dev = "设备id号"  # adb device 获取
        super().__init__()

    def setUp(self):
        print("custom setup")
        super(CustomAirtestCase, self).setUp()

    def tearDown(self):
        print("custom tearDown")
        # exec teardown script
        # self.exec_other_script("teardown.owl")
        super(CustomAirtestCase, self).setUp()

    def run_case1(self, data_item):
        """

        :param data_item: dict
        {'dev': 'emulator-5554', 'test_module': ['他的'], 'phone': '雷电', 'plat': 'android'}
        :return:
        """
        self.dev = data_item["dev"]
        # 记录测试设备
        MulCommon.set_case_module_dev({"test_dev": self.dev})
        # 记录测试模块
        for i in data_item["test_module"]:
            MulCommon.set_case_module_dev({"test_modules": i})

        get_case_data = MulCommon.get_cases(data_item, self.dev, self.root_path)
        if not get_case_data:
            return
        # 初始化安装的打开应用的情况，这里应该做适配比如ios,web等情况
        if data_item["platform"]=="android":
            init_android(data_item)
        elif data_item["platform"]=="web":
            print("执行web登录")
            get_driver(data_item["login_url"])
        # 循环执行用例
        for i in get_case_data:
            run(root_dir=self.root_path, test_case=i, device=self.dev, dev_connect=self.dev_connect,
                local_host_path=self.local_host_path, log_date=self.log_date,
                recording=self.recording, report_host=self.report_host, phone=data_item["phone"])

    def run_air(self, data):
        self.recording = data["recording"]
        self.report_host = "http://" + data["report_host"] + ":" + data["local_host_port"]
        # 开启本地http服务器
        thread_http = threading.Thread(target=HttpServer.start, args=(),
                                       kwargs={"local_host_path": data["local_host_path"],
                                               "port": data["local_host_port"]})
        thread_http.start()
        time.sleep(2)
        # 日志按照日期格式生成
        self.log_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # 生成本地的测试目录
        log_path = os.path.join(data["local_host_path"], "log")
        self.local_host_path = os.path.join(log_path, self.log_date)
        # remove_log表示如果传值就会删除整个log文件夹，删除后无法查看历史报告
        if data["remove_log"] and os.path.isdir(log_path):
            shutil.rmtree(log_path)
            ut_log.debug("%s 由于设置remove_log为真已经删除" % log_path)
        os.makedirs(self.local_host_path)
        print(str(self.local_host_path) + ' 日志根目录创建')

        # 整个用例开始执行时间
        start_time = datetime.now().strftime("%H:%M:%S")
        pool = Pool()
        # {'test_case': [{'dev': 'ZL9LC685V86DNNMN', 'test_module': ['我的'],'phone': '真机1', 'plat': 'android'}]}
        t_cases = data["test_case"]
        tm_cases = []
        # 由于使用map,需要把公共的一些参数合并进去
        for i in range(len(t_cases)):
            # 安卓和web处理参数不一致,因为安卓需要检查在线设备是否在线,若不在线就排除
            if data["platform"] == "android":
                # 有可能当前设备不可用，则排除不可用的设备
                if t_cases[i].get("dev") in data.get("dev_list"):
                    t_cases[i]["device"] = [data["dev_connect"] + t_cases[i]["dev"]]
                    t_cases[i]["platform"] = data["platform"]
                    t_cases[i]["save_image"] = data["save_image"]
                    t_cases[i]["pkg"] = data["pkg"]
                    t_cases[i]["apk"] = data["apk"]
                    t_cases[i]["install_type"] = data["install_type"]
                    t_cases[i]["test_plan"] = data["test_plan"]
                    t_cases[i]["boot"] = data["boot"]
                    t_cases[i]["dev_list"] = data["dev_list"]
                    tm_cases.append(t_cases[i])
                else:
                    ut_log.error(f"安卓不可用设备被排除,设备名称信息{t_cases[i]}")

            elif data["platform"] == "web":
                t_cases[i]["device"] = t_cases[i]["dev"]
                t_cases[i]["platform"] = data["platform"]
                t_cases[i]["save_image"] = data["save_image"]
                t_cases[i]["test_plan"] = data["test_plan"]
                t_cases[i]["boot"] = data["boot"]
                t_cases[i]["login_url"] = data["login_url"]
                tm_cases.append(t_cases[i])
        pool.map(self.run_case1, tm_cases)
        # 整个用例结束执行时间
        end_time = datetime.now().strftime("%H:%M:%S")
        # 以小时，分钟，秒钟的方式记录所有用例耗时时间
        total_time = get_case_total_time(start_time, end_time)
        #  得到测试用例的设备和模块，就是读取json文件
        test_modules_dev = MulCommon.get_case_module_dev(PATH("json/case_data.json"))

        # 计算用例成功，失败,总数
        get_case_data = MulCommon.get_result_json()
        # 记录成功的用例数
        success = 0
        # 记录用例总数
        s_count = len(get_case_data["data"])
        for j in get_case_data["data"]:
            if j.get("result"):
                success += 1

        # 记录用例结果
        MulCommon.set_result_summary_json({"start_time": self.log_date, "success": success, "count": s_count,
                                           "total_time": total_time, "phone": test_modules_dev["test_dev"],
                                           "modules": test_modules_dev["test_modules"], "dev": self.dev})

        # 生成测试报告
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.local_host_path),
            extensions=(),
            autoescape=True
        )
        ut_log.info("测试结果:%s" % MulCommon.get_result_json())
        # 先删除模板文件，然后拷贝进去，防止模板文件更新不及时
        t = os.path.join(self.local_host_path, "multi_summary_template.html")
        if os.path.exists(t):
            shutil.rmtree(t)
        shutil.copy(PATH("tpl/multi_summary_template.html"), self.local_host_path)

        template = env.get_template("multi_summary_template.html", self.local_host_path)
        html = template.render({"results": MulCommon.get_result_json()})
        put_html = os.path.join("summary_%s.html" % datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        output_file = os.path.join(self.local_host_path, put_html)
        with io.open(output_file, 'w', encoding="utf-8") as f:
            f.write(html)
        # 按日期生成测试报告,方便对比历史报告，但是程序入口字段需要设置为"remove_log": False
        ut_log.info("测试报告本地路径为：%s" % output_file)
        ut_log.info("测试报告访问服务器为：%s/%s/%s/%s" % (self.report_host, "log", self.log_date, put_html))
        thread_http.join()
        # 杀死chromedriver的进程,用driver.quit()就是退出当前进程
        os.system("taskkill /f /t /im chromedriver.exe")


def multi_runner(data1):
    fun_path = lambda p: os.path.abspath(
        os.path.join(os.path.dirname(__file__), p)
    )
    # 初始化记录数据的json
    MulCommon.init_result(fun_path("json/result_data.json"), fun_path("json/case_data.json"))

    run_case(data1)


if __name__ == '__main__':
    pass
    # PATH = lambda p: os.path.abspath(
    #     os.path.join(os.path.dirname(__file__), p)
    # )
    # path = PATH("config/setting1.ini")
    # data1 = ReadIni(path).get_ini_list()
    # if data1["boot"] == "multi":
    #     # 初始化记录数据的json
    #     Runner3Common.init_result(PATH("json/result_data.json"), PATH("json/case_data.json"))
    #     run_case(data1)
    # else:
    #     pass
