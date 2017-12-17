# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import ZhilianJobItem, ZhilianJobItemLoader
from ArticleSpider.utils.common import get_md5
import datetime

class ZhilianSpider(CrawlSpider):
    name = 'zhilian'
    allowed_domains = ['sou.zhaopin.com','jobs.zhaopin.com']
    start_urls = ["http://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E9%80%89%E6%8B%A9%E5%9C%B0%E5%8C%BA&kw=python&p=1&isadv=0"]

    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 0,
    }

    rules = (
        Rule(LinkExtractor(allow=r'jobs/.*'), follow=True),
        Rule(LinkExtractor(allow=r'\d+.htm.*'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """
        解析智联招聘的所有数据
        """
        item_loader = ZhilianJobItemLoader(item=ZhilianJobItem(), response=response)

        item_loader.add_xpath("title", "//*[@class='bread_crumbs']/a[3]/strong/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("min_salary","//*[@class='terminalpage-left']/ul/li[1]/strong/text()")
        item_loader.add_xpath("max_salary", "//*[@class='terminalpage-left']/ul/li[1]/strong/text()")
        item_loader.add_xpath("degree_need", "//*[@class='terminalpage-left']/ul/li[6]/strong/text()")
        item_loader.add_xpath("work_years", "//*[@class='terminalpage-left']/ul/li[5]/strong/text()")
        item_loader.add_xpath("job_city","//*[@class='terminalpage-left']/ul/li[2]/strong/a")
        item_loader.add_xpath("publish_time", "//*[@class='terminalpage-left']/ul/li[3]/strong")
        item_loader.add_css("comapany_name", ".company-name-t a::text")
        item_loader.add_xpath("company_advan", "//*[@class='top-fixed-box']/div[1]/div[1]/div[1]")
        item_loader.add_xpath("company_desc", "//*[@class='terminalpage-main clearfix']/div/div[2]")
        item_loader.add_xpath("job_desc", "/html/body/div[6]/div[1]/div[1]/div/div[1]")
        item_loader.add_value("crawl_time", datetime.datetime.now())

        zhilian_item = item_loader.load_item()
        return zhilian_item
