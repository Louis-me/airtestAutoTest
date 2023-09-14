# -*- coding=utf-8 -*-
import os
import time

from airtest_selenium.proxy import WebChrome
from selenium import webdriver
from util.read_ini1 import ReadIni
from util.log_util import log as ut_log
from util.selenium_driver import Element
from selenium.webdriver.common.keys import Keys


def get_selenium_driver():
    """
    得到driver
    :return:
    """
    r_data = ReadIni.get_web()
    chrome_exe = r_data.get("chrome_exe")
    chrome_driver = r_data.get("chrome_driver")
    if not os.path.exists(chrome_exe):
        print("请检chrome.exe文件是否存在：%s" % r_data["chrome_exe"])
        return
    if not os.path.exists(chrome_driver):
        print("请检查驱动文件是否存在：%s" % r_data["chrome_driver"])
        return
    os.environ["webdriver.chrome.driver"] = chrome_driver
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_exe
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')

    driver = WebChrome(chrome_driver, options=options)
    driver.maximize_window()
    time.sleep(3)
    # 全局等待30秒
    driver.implicitly_wait(30)
    return driver


def sel_login(driver, url="http://www.shikun.work:8001/#/login"):
    try:
        driver.get(url)
        time.sleep(3)
        if not driver.find_element_by_xpath("//input[@type='text']").is_displayed():
            driver.get(url)
            print("重新打开一个网址")
            time.sleep(3)
        driver.find_element_by_xpath("//input[@type='text']").click()
        time.sleep(1)

        driver.find_element_by_xpath("//input[@type='text']").send_keys("test1")
        time.sleep(1)

        driver.find_element_by_xpath("//input[@type='password']").click()
        time.sleep(1)

        driver.find_element_by_xpath("//input[@type='password']").send_keys("123456")
        time.sleep(1)
        driver.find_element_by_xpath("//*[@id=\"app\"]/div/div/form/div[3]/div/button").click()
        time.sleep(1)
        driver.find_element_by_xpath('//span[contains(text(),"用户管理")]').click()
        return True
    except Exception as e:
        print("登录失败")
        ut_log.error("登录失败,%s" % str(e))
        return False


def get_driver(url="http://www.shikun.work:8001/#/login"):

    if not Element.driver:
        print("未登录,登录中")
        Element.driver = get_selenium_driver()
        sel_login(Element.driver, url)
        print(Element.driver)
    else:
        print("登录了？")
        print(Element.driver)
    return Element.driver

def get_driver1(url="http://www.shikun.work:8001/#/login"):

    dr = get_selenium_driver()
    sel_login(dr, url)
    return dr


