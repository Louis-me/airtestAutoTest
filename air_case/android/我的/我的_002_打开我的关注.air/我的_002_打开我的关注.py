# -*- encoding=utf8 -*-
__author__ = "Administrator"

from airtest.core.api import *
import sys

# 得到绝对路径
from selenium_driver import Element

abs_path = os.path.abspath(os.path.dirname(__file__))
# 得到公共用例目录
common_path = os.path.join(abs_path.split("airtestAutoTest")[0], "airtestAutoTest", "util")
sys.path.append(common_path)
from app_util import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

print("----打印poco--真机-")
print(Element.poco)
def operate():
    auto_setup(__file__)
    poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
    # poco = Element.poco
    start_app("com.jianshu.haruki")

    try:
    # 初始化用例
    # init_app()
        # 得到上级目录
        path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        # 得到用例名称,用例配置文件一般和用例名字保持一致
        case_name = os.path.basename(__file__).strip(".py") + ".yml"
        # 得到用例目录
        case_path = os.path.join(path, "yml", case_name)
        # 执行用例
        operate_test_case(poco, case_path)
    except Exception as e:
        # snapshot(msg="报错后截图")
        raise e


operate()
