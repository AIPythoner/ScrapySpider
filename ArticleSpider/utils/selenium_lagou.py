import requests
import time
from selenium import webdriver
from scrapy.selector import Selector

url = "https://passport.lagou.com/login/login.html"

def selenium_zhihu_login():
    """
    selenium 模仿登陆拉钩
    """
    browser = webdriver.Chrome(executable_path="F:\python项目开发\软件\chromedriver.exe")
    browser.get(url)
    browser.find_element_by_css_selector(".active input[placeholder='请输入常用手机号/邮箱']").send_keys("18299536448")
    browser.find_element_by_css_selector(".active input[placeholder='请输入密码']").send_keys("zdj515158.")
    browser.find_element_by_css_selector(".active  input.btn_green").click()
    time.sleep(10)
    cookies = browser.get_cookies()
    print(cookies)
    cookie = [item["name"] + "=" + item["value"] for item in browser.get_cookies()]
    print(cookie)
    cookiestr = ';'.join(item for item in cookie)
    print(cookiestr)
    headers = {"cookie":cookiestr}

    new_dic = {}
    for i in browser.get_cookies():
        new_dic[i["name"]] = i["value"]
    response_new = requests.get("https://www.lagou.com/s/subscribe.html", cookies=new_dic)
    response = requests.get("https://www.lagou.com/s/subscribe.html", headers=headers)
    # print(response.text)
    a =  1

    browser.quit()
selenium_zhihu_login()