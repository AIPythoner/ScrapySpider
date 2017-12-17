# coding=utf-8
import json
import requests


class YDMHttp():
    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username, password, appid, appkey):
        self.username = username
        self.password = password
        self.appid = appid
        self.appkey = appkey

    def balance(self):
        data = {'method':'balance', 'username':self.username,
                'password':self.password, 'appid':self.appid, 'appkey':self.appkey}
        response_data = requests.post(self.apiurl, data=data)
        ret_data = json.loads(response_data.text)
        if ret_data['ret'] == 0:
            print("获取剩余积分", ret_data['balance'])
            return ret_data['balance']

    def login(self):
        data = {"method": "login", "username": self.username,
                "password": self.password, "appid": self.appid, "appkey": self.appkey}
        response_data = requests.post(self.apiurl, data=data)
        ret_data = json.loads(response_data.text)
        if ret_data['ret'] == 0:
            print("登陆成功", ret_data['uid'])
            return ret_data['uid']
        else:
            return None

    def decode(self,filename, codetype, timeout):
        data = {"method": "upload", "username": self.username,"password": self.password, "appid": self.appid,
                "appkey": self.appkey, 'codetype': str(codetype), "timeout": str(timeout)}
        files = {'file':open(filename, 'rb')}
        response_data = requests.post(self.apiurl, files=files, data=data)
        ret_data = json.loads(response_data.text)
        if ret_data['ret'] == 0:
            print("识别成功", ret_data['text'])
            return ret_data['text']
        else:
            return None


def ydm(file_path):
    username = 'suyajie'
    password = 'zdj515158.'
    appid = 4234
    appkey = 'eaba1ae96d5f653ff125938f5809cee8'
    codetype = 5000
    timeout = 60

    ydm_yzm = YDMHttp(username, password, appid, appkey)
    if username == 'username':
        print("请设置好相关参数后在调试")
    else:
        return ydm_yzm.decode(file_path, codetype, timeout)

# print(ydm(r'..\..\captcha.jpg'))

# if __name__ == "__main__":
#     username = 'suyajie'
#     password = 'zdj515158.'
#     appid = 4234
#     appkey = 'eaba1ae96d5f653ff125938f5809cee8'
#     filename = 'captcha.jpg'
#     codetype = 5000
#     timeout = 60
#     if username == 'username':
#         print("请设置好相关参数后在调试")
#     else:
#         yundama = YDMHttp(username, password, appid, appkey)
#
#         uid = yundama.login();
#         print('uid: %s' % uid)
#
#         # 登陆云打码
#         uid = yundama.login();
#         print ('uid: %s' % uid)
#
#         # 查询余额
#         balance = yundama.balance();
#         print ('balance: %s' % balance)
#
#         # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
#         text = yundama.decode(filename, codetype, timeout)
#
#         pass
#
