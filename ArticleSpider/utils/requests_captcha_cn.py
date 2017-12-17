import requests
import re
import http.cookiejar as cookielib
from zheye import zheye

z = zheye()
positions = z.Recognize('captcha.jpg')

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookie.json")

try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")


headers = {
   "Host": 'www.zhihu.com',
   'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64 ; rv:56.0) Gecko/20100101 Firefox/56.0",
   "Referer": 'https://www.zhihu.com',
}



def is_login():
    in_box = "https://www.zhihu.com/settings/profile"
    response = session.get(in_box, headers=headers, allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True

def captcha():
    import time
    t = str(int(time.time()*1000))

    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn"
    t = session.get(captcha_url, headers=headers)
    with open("captcha.jpg","wb") as f:
        f.write(t.content)
        f.close()
    from PIL import Image
    try:
        im = Image.open("captcha.jpg")
        im.show()
        im.close()
    except:
        pass


def get_xsrf():
    response = session.get(url="https://www.zhihu.com/",headers=headers)
    text = response.text
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', text)
    xsfr_code = ''
    if match_obj:
        xsfr_code = match_obj.group(1)
    return xsfr_code


def zhihu_login(account, password):
    if re.match("^1\d{10}", account):
        print("手机号码登陆")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,


        }
    response_text = session.post(post_url, data=post_data, headers=headers)
    session.cookies.save()

#zhihu_login("18299536448", "zdj515158.")
captcha()


def login_after_captcha_cn(self, response):
    # 验证知乎倒立汉字
    with open("captcha.jpg", "wb") as f:
        f.write(response.body)
        f.close()
    from PIL import Image
    from zheye import zheye
    z = zheye()
    positions = z.Recognize('captcha.jpg')

    pos_arr = []
    if len(positions) == 2:
        pos_arr = [[positions[0][1], positions[0][0]], [positions[1][1], positions[1][0]]]
    else:
        pos_arr.append([positions[0][1], positions[0][0]])

    post_data = response.meta.get("post_data", {})
    post_url = "https://www.zhihu.com/login/phone_num"
    if len(positions) == 2:
        post_data["captcha"] = '{"img_size":[200,44], "input_points":[[%.2f, %.2f], [%.2f, %.2f]]}' % (
            pos_arr[0][0] / 2, pos_arr[0][1] / 2, pos_arr[1][0] / 2, pos_arr[1][1] / 2
        )
    else:
        post_data["captcha"] = '{"img_size"[200,44], "input_points":[[%.2f, %.2f]]}' % (
            pos_arr[0][0] / 2, pos_arr[0][1] / 2
        )
    post_data["captcha_type"] = "cn"
    a = 1
    return [scrapy.FormRequest(
        url=post_url,
        formdata=post_data,
        headers=self.headers,
        callback=self.check_login,
    )]