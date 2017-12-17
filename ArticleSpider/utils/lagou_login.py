import re
import requests

headers = {
   "Host": 'www.zhihu.com',
   'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64 ; rv:56.0) Gecko/20100101 Firefox/56.0",
   "Referer": 'https://www.lagou.com/',
}

def lagou_login(account, password):
    if re.match("^1\d{10}", account):
        print("手机号码登陆")
        post_url = "https://passport.lagou.com/login/login.json"
        post_data = {
            "isValidate": "true",
            "username": account,
            "password": password,
        }
    response_text = requests.post(post_url, data=post_data, headers=headers)
    pass

lagou_login("18299536448","d1730b3f1bb7505ca4df92507ba1faf0")