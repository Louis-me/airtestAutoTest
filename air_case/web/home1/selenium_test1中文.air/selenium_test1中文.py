# -*- encoding=utf8 -*-
from airtest.core.api import *
import sys
# pip3 install pynput
# pip3 install airtest-selenium
# 得到绝对路径

abs_path = os.path.abspath(os.path.dirname(__file__))
# 得到公共用例目录
common_path = os.path.join(abs_path.split("airtestAutoTest")[0], "airtestAutoTest", "web_util")
sys.path.append(common_path)
from web_util import *
# driver = WebChrome()
driver = get_driver()

try:
    print("----test1-----")
    print(driver)
    driver.get(r"http://www.shikun.work:8001/#/welcome")
    sleep(1)
    driver.find_element_by_xpath('//span[contains(text(),"用户管理")]').click()
    sleep(1)

    driver.find_element_by_xpath('//span[contains(text(),"用户列表")]').click()
    sleep(1)

    driver.find_element_by_css_selector("input").send_keys("test111")
    sleep(1)

    driver.find_element_by_xpath('//i[@class="el-icon-search"]').click()
    # driver.close()
except Exception as e:
    driver.snapshot()
    print("test1失败了")
    print(str(e))
    raise e
# finally:
#     driver.close()