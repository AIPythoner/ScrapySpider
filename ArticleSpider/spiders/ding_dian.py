# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'dd'
    # allowed_domains = ["x23us.com/"] #这里域名过滤有问题
    start_urls = ['https://www.x23us.com/']

    def parse(self, response):

        book_list = response.css('.poptext::attr(href)').extract()
        for post_node in book_list:
            yield Request(post_node, callback=self.book)

        # 提取下一页并交给scrapy进行下载
        # next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        # if next_url:
        #      yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def book(self, response):
        url = response.url
        number = response.css(".L a::attr(href)").extract()[0]
        postUrl = url + number
        yield Request(postUrl,callback=self.parse_detail)
        if response.xpath('//*[@id="footlink"]/a[3]/text()').extract()[0] == u'下一页':
            number = int(number.replace(".html",""))
            postUrl = url + str((number+1)) + '.html'
            yield Request(postUrl, callback=self.parse_detail)

    def parse_detail(self, response):

        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()

        yield article_item