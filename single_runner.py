# -*- coding=utf-8 -*-
import shutil
import threading

from airtest.cli.runner import AirtestCase, run_script
from argparse import *
import jinja2
import io
from airtest.report import report
from util.android_util import attached_devices
from util.common import *
from util.http_server import HttpServer
from util.android_util import init_android
from util.log_util import log as ut_log
from util.web_util import get_selenium_driver, sel_login
from util.selenium_driver import Element


PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


def run_case(data1: dict):
    get_data_list = get_test_case(data1)
    if not get_data_list:
        ut_log.error("无可用用例")
        return
    # 读取用例列表
    data1["case_list"] = get_data_list
    # 当平台为安卓时，检查是否连接成功
    device = None
    if data1.get("platform", "1") == "android":
        ut_log.debug("安卓启动器,目标连接设备内容id为%s" % data1["dev"])
        ad_devices = attached_devices()
        if not ad_devices:
            ut_log.error("无可用设备")
            return
        if data1["dev"] not in ad_devices:
            ut_log.error("请检查设备%s是否正常连接" % data1["dev"])
            return
        device = [data1["dev_connect"] + data1["dev"]]
        # Android://127.0.0.1:5037/emulator-5554
        # 设置安卓的连接字符串
        data1["device"] = device
        # 初始化安装的打开应用的情况
        init_android(data1)
    elif data1.get("platform", "1") == "ios":
        pass
    elif data1.get("platform", "1") == "web":
        print("启动web启动器")
        ut_log.debug("web启动器")
        # 初始化web的打开应用的情况
        #启动driver
        Element.driver=get_selenium_driver()
        # 先进行登录操作，若登录失败后续操作就不进行
        clogin = sel_login(Element.driver, data1.get("login_url"))
        if not clogin:
            return
        data1["device"] = device

    test = CustomAirtestCase()
    # data1 为多个配置文件ini的合并
    test.run_air(data1)


def run(root_path, test_case, device, local_host_path, recording=None):
    """

    :param root_path: 用例根目录
    :param test_case: dict|{"case": "111.air", "module": "小回归"}
    :param device: Android://127.0.0.1:5037/emulator-5554
    :param local_host_path: airtest/report源代码目录
    :param recording: 是否录屏
    :return:
    """
    # 具体的用例
    script = os.path.join(root_path, test_case["module"], test_case["case"])
    case_path = os.path.join(test_case["module"], test_case["case"].replace('.air', ''))
    log = os.path.join(local_host_path, case_path)
    os.makedirs(log)
    # print(str(log) + '日志文件目录创建成功')
    output_file = os.path.join(log, 'log.html')
    args = Namespace(device=device, log=log, compress=None, recording=recording, script=script, no_image=None)
    try:
        tt = run_script(args, AirtestCase)
        print("runtest-ss")
        print(tt)
        is_success = True
    except:
        is_success = False

    return {"is_success": is_success, "output_file": output_file, "script": script, "log": log}


class CustomAirtestCase(AirtestCase):
    @classmethod
    def setUpClass(cls):
        super(CustomAirtestCase, cls).setUpClass()

    def __init__(self):
        # 记录失败用例数据
        self.fail_data = []
        # 初始化记录测试结果
        self.results = {"dev": "", "modules": [], "total_time": "", "data": [], "start_time": "", "success": "",
                        "count": ""}
        super().__init__()

    def setUp(self):
        super(CustomAirtestCase, self).setUp()

    def tearDown(self):
        print("custom tearDown")
        super(CustomAirtestCase, self).setUp()

    def run_air(self, data: dict):
        # 开启本地http服务器
        threading.Thread(target=HttpServer.start, args=(),
                         kwargs={"local_host_path": data["local_host_path"], "port": data["local_host_port"]}).start()
        # 整个用例开始执行时间
        start_time = datetime.now().strftime("%H:%M:%S")
        # 组成为ip访问的地址http://ip:port
        data['report_host'] = "http://" + data["report_host"] + ":" + data["local_host_port"]
        # 模块名称
        modules = []
        # 日志按照日期格式生成
        log_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # 生成本地记录日志的目录
        log_path = os.path.join(data["local_host_path"], "log")
        local_host_path = os.path.join(log_path, log_date)
        # remove_log表示如果传值就会删除整个log文件夹，删除后无法查看历史报告
        if data["remove_log"] and os.path.isdir(log_path):
            shutil.rmtree(log_path)
            ut_log.debug("%s 由于设置remove_log为真已经删除" % log_path)
        os.makedirs(local_host_path)
        print(str(local_host_path) + '日志根目录创建成功')

        # 开始循环运行用例

        # 用例列表
        case_list = data.get("case_list")
        for j in case_list:
            # 用例开始执行日期
            st_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 用例开始执行时间
            s_time = datetime.now().strftime("%H:%M:%S")
            # 循环运行用例
            get_run = run(data["root_path"], j, data["device"], local_host_path, data["recording"])
            # 用例结束执行日期
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 用例结束执行时间
            e_time = datetime.now().strftime("%H:%M:%S")
            # 用例耗时时间
            sum_time = get_case_total_time(s_time, e_time)
            # 生成测试用例的详情报告
            # plugins=['airtest_selenium.report']加入支持selenium,如果不加那么截图无法展示,等到用例稳定后建议去掉这里防止图片太多
            rpt = report.LogToHtml(script_root=get_run["script"], log_root=get_run["log"],
                                   static_root=data["report_host"])
            rpt.report("log_template.html", output_file=get_run["output_file"])
            # 记录测试结果
            s_name = os.path.join(j["case"].replace(".air", ""))
            s_log = os.path.join(data["report_host"], "log", log_date, j["module"], s_name)
            result = {"result": get_run["is_success"], "start_date": st_date, "end_date": end_date,
                      "sum_time": sum_time, "log": s_log, "name": s_name}
            # 记录模块名称
            modules.append(j["module"])
            self.results["data"].append(result)
            # 记录失败用例
            if not get_run["is_success"]:
                self.fail_data.append({"module": j["module"], "case": j["case"]})
        # 整个用例结束执行时间
        end_time = datetime.now().strftime("%H:%M:%S")
        # 以小时，分钟，秒钟的方式记录所有用例耗时时间
        total_time = get_case_total_time(start_time, end_time)
        self.results["total_time"] = total_time
        # 记录测试模块
        self.results["modules"] = get_test_modules(modules)
        # 记录设备名字
        self.results["phone"] = data["phone"]
        # 计算用例成功，失败,总数
        get_case_data = self.results["data"]
        success = 0
        s_count = len(get_case_data)
        for j in get_case_data:
            if j.get("result"):
                success += 1
        self.results["start_time"] = log_date
        self.results["success"] = success
        self.results["count"] = s_count
        self.results["dev"] = data["dev"]

        # 打印失败用例
        if self.fail_data:
            ut_log.error("存在失败用例：%s" % self.fail_data)

        # 生成测试报告
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(local_host_path),
            extensions=(),
            autoescape=True
        )
        ut_log.info("用例结果为：%s" % self.results)
        # 可能模板文件已经更新，所以要先删除模板文件
        t = os.path.join(local_host_path, "summary_template.html")
        if os.path.exists(t):
            shutil.rmtree(t)
        shutil.copy(PATH("tpl/summary_template.html"), local_host_path)
        template = env.get_template("summary_template.html", local_host_path)
        html = template.render({"results": self.results})
        put_html = os.path.join("summary_%s.html" % datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        output_file = os.path.join(local_host_path, put_html)
        with io.open(output_file, 'w', encoding="utf-8") as f:
            f.write(html)
        # 按日期生成测试报告,方便对比历史报告，但是程序入口字段需要设置为"remove_log": False
        ut_log.info("测试报告本地路径：%s" % output_file)
        ut_log.info("测试报告访问服务器：%s/%s/%s/%s" % (data['report_host'], "log", log_date, put_html))
        if data["platform"] == "android":
            Element.driver.close()
            Element.driver.quit()
        # # 固定输出给CI
        # output_file = os.path.join(data["root_path"], "summary.html")
        # with io.open(output_file, 'w', encoding="utf-8") as f:
        #     f.write(html)
        # 当发送邮件参数为真，就对文件进行压缩并发送测试报告到指定邮箱，此功能暂时不做适配
        if data.get("send_email"):
            # 压缩测试报告
            # report_file = os.path.join(data["root_path"], "report")
            # case_log = os.path.join(data["root_path"], "log")
            # case_html = output_file
            # zip_list = [report_file, case_log, case_html]
            # zip_path = copy_and_zip(zip_list, "report")
            # # 发送测试报告邮件
            # to_addr = data["to_addr"]
            # SendEmail.send(zip_path=zip_path, to_addr=to_addr)
            pass


def single_runner(data1):
    run_case(data1)

# if __name__ == '__main__':
#     PATH = lambda p: os.path.abspath(
#         os.path.join(os.path.dirname(__file__), p)
#     )
#     path = PATH("config/setting1.ini")
#     data = ReadIni(path).get_ini_list()
#     run_case(data)
