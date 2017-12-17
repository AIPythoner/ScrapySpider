# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from ArticleSpider.items import LagouJobItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com','https://www.lagou.com/jobs/list_python']
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.lagou.com",
        "Upgrade-Insecure-Requests": "1",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    }
    custom_settings = {
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY" : 0.1,
    }

    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def __init__(self):
        self.browser = webdriver.Chrome(executable_path="F:\python项目开发\软件\chromedriver.exe")
        super(LagouSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候退出chrome
        print("spider closed")
        self.browser.quit()

    def start_requests(self):
        cookie_dict = {}
        self.browser.get("https://passport.lagou.com/login/login.html")
        self.browser.find_element_by_css_selector(".active input[placeholder='请输入常用手机号/邮箱']").send_keys("1829******8")
        self.browser.find_element_by_css_selector(".active input[placeholder='请输入密码']").send_keys("********")
        self.browser.find_element_by_css_selector(".active  input.btn_green").click()
        time.sleep(20)

        for i in self.browser.get_cookies():
            cookie_dict[i["name"]] = i["value"]

        return [scrapy.Request(url=self.start_urls[1],headers=self.headers, cookies=cookie_dict, callback=self.parse)]

    def parse_job(self, response):
        itemloader = LagouJobItemLoader(item=LagouJobItem(),response=response)

        itemloader.add_css("title", ".job-name::attr(title)")
        itemloader.add_value("url", response.url)
        itemloader.add_value("url_object_id", get_md5(response.url))
        itemloader.add_css("salary", ".job_request .salary::text")

        itemloader.add_xpath("job_city" ,"//*[@class='job_request']/p/span[2]/text()")
        itemloader.add_xpath("work_years" ,"//*[@class='job_request']/p/span[3]/text()")
        itemloader.add_xpath("degree_need" ,"//*[@class='job_request']/p/span[4]/text()")
        itemloader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        itemloader.add_css("tags", ".position-label li::text")
        itemloader.add_css("publish_time", ".publish_time::text")
        itemloader.add_css("job_adnvantage", ".job-advantage p::text")
        itemloader.add_css("job_desc", ".job_bt div")
        itemloader.add_css("job_addr", ".work_addr")
        itemloader.add_css("company_name", "#job_company dt a img::attr(alt)")
        itemloader.add_css("company_url", "#job_company dt  a::attr(href)")
        itemloader.add_value("crawl_time", datetime.datetime.now())

        job_item = itemloader.load_item()

        return job_item
