# -*- encoding=utf8 -*-
__author__ = "Administrator"

from airtest.core.api import *
import sys
# pip3 install pynput
# pip3 install airtest-selenium
abs_path = os.path.abspath(os.path.dirname(__file__))
common_path = os.path.join(abs_path.split("airtestAutoTest")[0], "airtestAutoTest", "web_util")
sys.path.append(common_path)
from web_util import *

# driver = WebChrome()
driver = get_driver()
try:
    print("----test2-----")
    print(driver)
    driver.get(r"http://www.shikun.work:8001/#/welcome")
    sleep(1)

    driver.find_element_by_xpath('//span[contains(text(),"用户管理")]').click()
    sleep(1)

    driver.find_element_by_xpath('//span[contains(text(),"用户列表1")]').click()
    sleep(1)

    driver.find_element_by_css_selector("input").send_keys("test222")
    sleep(1)

    driver.find_element_by_xpath('//i[@class="el-icon-search"]').click()
    # driver.close()
except Exception as e:
    driver.snapshot()
    print("test2失败了")
    print(str(e))
    raise e

# finally:
#     driver.close()
