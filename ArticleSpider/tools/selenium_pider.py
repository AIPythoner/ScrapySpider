import time
from selenium import webdriver
from scrapy.selector import Selector

def selenium_zhihu_login():
    """
    selenium 模仿知乎登陆
    """
    browser = webdriver.Chrome(executable_path="F:\python项目开发\软件\chromedriver.exe")
    browser.get("https://www.zhihu.com/#signin")
    browser.find_element_by_css_selector(".qrcode-signin-step1 span.signin-switch-password").click()
    browser.find_element_by_css_selector(".view-signin input[name='account']").send_keys("18299536448")
    browser.find_element_by_css_selector(".view-signin input[name='password']").send_keys("zdj515158.")
    browser.find_element_by_css_selector(".view-signin button.sign-button").click()
    browser.quit()

def selenium_weibo_login():
    """
    selenium模仿微博登陆
    """
    browser = webdriver.Chrome(executable_path="F:\python项目开发\软件\chromedriver.exe")
    browser.get("http://www.weibo.com/")
    time.sleep(15)
    browser.find_element_by_css_selector("#loginname").send_keys("15678515158")
    browser.find_element_by_css_selector(".info_list.password input[name='password']").send_keys("krzz1937")
    browser.find_element_by_css_selector('.info_lista.login_btn a[node-type="submitStates"]').click()
    browser.execute_script("window.scrollTo(0, doucument.body.scrollHeight; var lenOfPage=document.body.scrollHeight; return lenOfPage)")

def kaiyuanzhongguo():
    browser = webdriver.Chrome(executable_path="F:\python项目开发\软件\chromedriver.exe")
    browser.get("https://www.oschina.net/blog")
    for i in range(3):
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage")
        time.sleep(3)

def no_download_img():
    #不加载图片
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(executable_path="F:\python项目开发\软件\chromedriver.exe",chrome_options=chrome_options)
    browser.get("https://www.taobao.com")

no_download_img()

def phantomjs():
    #phantomjs, 无界面浏览器，多进程的情况下phantomjs性能下降严重
    browser = webdriver.PhantomJS(executable_path="F:\python项目开发\软件\chromedriver.exe")
    browser.get("https://www.taobao.com")
    pass