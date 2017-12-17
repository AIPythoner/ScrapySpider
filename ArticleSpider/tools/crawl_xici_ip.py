import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="localhost", user="root", passwd="krzz1937", db="scrapyspider", charset="utf8")
cursor = conn.cursor()


def crawl_ip():
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0",
    }

    for i in range(1,2500):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i),headers=headers)
        selector = Selector(text=re.text)
        ip_list = []
        all_trs = selector.css("#ip_list tr")[1:]

        for tr in all_trs:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])

            all_text = tr.css("td::text").extract()
            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]
            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert ip_pool(ip, port, proxy_type, speed) VALUES('{0}', '{1}', '{2}', {3})  ON DUPLICATE KEY UPDATE port=VALUES(port), proxy_type=VALUES(proxy_type), speed=VALUES(speed)".format(
                                ip_info[0], ip_info[1], ip_info[2], ip_info[3])
            )
            conn.commit()




class GetIP(object):
    def delete_ip(self, ip):
        delete_sql = """
            delete from ip_pool where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()

    def judge_ip(self, ip, port):
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
            pass
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >=200 and code <300:
                print("effective ip ")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        #从数据库中随机获得一个ip
        random_sql = """
            SELECT ip, port  FROM ip_pool
            ORDER BY RAND()
            LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_result = self.judge_ip(ip, port)
            if judge_result:
                return "http://{0}:{1}".format(ip ,port)
            else:
                self.get_random_ip()

if __name__ == "__main__":
    get_ip = GetIP()
    get_ip.get_random_ip()
