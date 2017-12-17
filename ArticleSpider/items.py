# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import re
import redis
import datetime
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from ArticleSpider.models.es_types import ArticleType
from elasticsearch_dsl.connections import connections
from w3lib.html import remove_tags

es = connections.create_connection(ArticleType._doc_type.using)
redis_cli = redis.StrictRedis()


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


def get_nums(text):
    match_obj = re.match(".*?(\d+).*",text)
    if match_obj:
        return int(match_obj.group(1))
    else:
        return 0


def remove_comment_tags(text):
    if "评论" in text:
        return ""
    else:
        return text

def date_convert(value):
    text = value.strip().replace('·', "").strip()
    try:
        create_date = datetime.datetime.strptime(text, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date

def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={"filter":["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})
    return suggests

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def save_to_es(self):
        #存储到es中
        article = ArticleType()
        article.title = self["title"]
        article.create_date = self["create_date"]
        article.content = remove_tags(self["content"])
        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.praise_nums = self["praise_nums"]
        article.fav_nums = self["fav_nums"]
        article.comment_nums = self["comment_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.meta.id = self["url_object_id"]

        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10),(article.tags, 7)))

        article.save()
        redis_cli.incr("jobbole_count")
        return

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, content, comment_nums, create_date, front_image_url, fav_nums, praise_nums, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            
            ON DUPLICATE KEY UPDATE comment_nums=VALUES(comment_nums), fav_nums=VALUES(fav_nums), praise_nums=VALUES(praise_nums)
            """
        params = (self["title"], self["url"], self["url_object_id"], self["content"], self["comment_nums"],
                  self["create_date"], self["front_image_url"], self["fav_nums"], self["praise_nums"], self["tags"])
        return insert_sql, params



class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field( )
    comments_num = scrapy.Field( )
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
            insert into zhihui_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.datetime.now()

        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = self["title"][0]
        content = self["content"][0]
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))
        crawl_time= datetime.datetime.now()

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = int(self["watch_user_num"][1])
        else:
            watch_user_num = int(self["watch_user_num"][0])
            click_num = 0

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time, update_time, crawl_time
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
              update_time=VALUES(update_time)
        """

        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        crawl_time = datetime.datetime.now()
        params = (
            self["zhihu_id"], self["url"], self["question_id"], self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time, self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )
        return insert_sql, params


def remove_splash(value):
    #去掉斜杠
    return value.replace("/", "")


def remove_job_addr_space(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图" ]
    return "".join(addr_list)


def remove_pulish_time_word(value):
    return value.replace("发布于拉勾网", "")


def min_max_salary(value):
    try:
        min_obj = int(re.match(".*?(\d+)k", value).group(1))
        max__obj = int(re.match(".*?-(\d+)k", value).group(1))
    except Exception as e:
        min_obj = 0
        max__obj = 0
    return min_obj, max__obj

class LagouJobItem(scrapy.Item):
    """
    拉钩网的职位信息
    """
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field(
        input_processor=MapCompose(remove_pulish_time_word)
    )
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    job_adnvantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_job_addr_space)
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):

        min_salary, max_salary = min_max_salary(self["salary"])
        insert_sql = """
            insert into lagou(title, url, url_object_id, salary, job_city, work_years, degree_need, job_type, publish_time,
            tags, job_adnvantage, job_desc, job_addr, company_url, company_name, crawl_time, min_salary, max_salary)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
             ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_city=VALUES(job_city), work_years=VALUES(work_years),
              degree_need=VALUES(degree_need), job_type=VALUES(job_type), publish_time=VALUES(publish_time), tags=VALUES(tags)
              , job_adnvantage=VALUES(job_adnvantage), job_desc=VALUES(job_desc), crawl_time=VALUES(crawl_time),
                min_salary=VALUES(min_salary), max_salary=VALUES(max_salary)
        """
        param = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"], self["work_years"],
            self["degree_need"], self["job_type"], self["publish_time"], self["tags"], self["job_adnvantage"], self["job_desc"], self["job_addr"],
            self["company_url"], self["company_name"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT), min_salary, max_salary
        )

        return insert_sql, param


class LagouJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


def remove_strip(value):
    return value.strip().replace("\r","").replace("\n","").replace(" ","")


def min_salary(value):
    try:
        min_ = int(re.match("(\d+)-", value).group(1))
    except Exception as e:
        min_ = 0
    return min_


def max_salary(value):
    try:
        max_ = int(re.match(".*-(\d+)",value).group(1))
    except Exception as e:
        max_ = 0
    return max_


def work_years(value):
    if "不限" in value:
        return 0
    try:
        years = re.match("(\d+)-",value).group(1)
    except Exception as e:
        years = 99
    return years


def publish_time(value):
    if re.match("000.*", value):
            return datetime.datetime.now().date().strftime("%Y-%m-%d")
    return value


class ZhilianJobItemLoader(ItemLoader):
    #智联自定义的Itemloader
    default_output_processor = TakeFirst()


class ZhilianJobItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    min_salary = scrapy.Field(
        input_processor=MapCompose(min_salary)
    )
    max_salary = scrapy.Field(
        input_processor=MapCompose(max_salary)
    )
    publish_time = scrapy.Field(
        input_processor=MapCompose(remove_tags, publish_time)
    )
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_strip)
    )
    degree_need = scrapy.Field()
    work_years = scrapy.Field(
        input_processor=MapCompose(work_years)
    )
    comapany_name = scrapy.Field()
    company_advan = scrapy.Field(
        input_processor=MapCompose(remove_tags)
    )
    company_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_strip)
    )

    crawl_time = scrapy.Field()
    def get_insert_sql(self):

        insert_sql = """
            insert into zhilian(title, url, url_object_id, min_salary, max_salary, publish_time, job_city, job_desc, degree_need,
            work_years, company_name, company_advan, company_desc, crawl_time)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
             ON DUPLICATE KEY UPDATE min_salary=VALUES(min_salary), max_salary=VALUES(max_salary), publish_time=VALUES(publish_time),
              work_years=VALUES(work_years), company_advan=VALUES(company_advan), publish_time=VALUES(publish_time),
              job_desc=VALUES(job_desc), crawl_time=VALUES(crawl_time), title=VALUES(title)
                
        """
        param = (
            self["title"], self["url"], self["url_object_id"], self["min_salary"], self["max_salary"],
            self["publish_time"],self["job_city"], self["job_desc"], self["degree_need"], self["work_years"],
            self["comapany_name"], self["company_advan"],self["company_desc"],
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql, param