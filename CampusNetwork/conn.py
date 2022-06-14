import requests
import argparse
import logging
import time
import json
import re

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
    filename='conn.log',
    filemode='w'
)


class getHtmlElement:
    """
    二个api分别是用于获取渲染网页的html代码和json格式的运营商选项
    此部分没有涉及到校园网的自动连接
    """

    def __init__(self):
        self.pageInfo = 'http://10.100.1.5/eportal/InterFace.do?method=pageInfo'  # 网页信息API
        self.Services = 'http://10.100.1.5/eportal/InterFace.do?method=getServices'  # 获取运行商选项
        self.query = "wlanuserip=null&wlanacname=null&ssid=null&nasip=null&snmpagentip=null&mac=null&t=null&url=null&apmac=null&nasid=null&vid=null&port=null&nasportid=null"
        self.postData = {
            'queryString': ''  # 默认提交空信息，如果需要请使用query
        }

    def getPageInfo(self):
        response = requests.post(self.pageInfo, headers=header, data=self.postData)
        print(response.status_code)
        print(response.content.decode('utf-8', 'ignore'))

    def getServices(self):
        response = requests.post(self.Services, headers=header)
        print(response.status_code)
        print(response.content.decode('utf-8', 'ignore'))


class conn:
    url = 'http://10.100.1.5'
    OnlineUserInfo = 'http://10.100.1.5/eportal/InterFace.do?method=getOnlineUserInfo'  # 获取当前网络连接状态
    ErrorMsg = 'http://10.100.1.5/eportal/userV2.do?method=getErrorMsg'  # 登录后获取错误信息
    login = 'http://10.100.1.5/eportal/InterFace.do?method=login'  # 登录网页
    logout = 'http://10.100.1.5/eportal/InterFace.do?method=logout'  # 退出网页

    # use urllib.parse.quote_plus to encode character first
    service = {
        'campus': '%E6%A0%A1%E5%9B%AD%E7%BD%91',
        'telecom': '%E4%B8%AD%E5%9B%BD%E7%94%B5%E4%BF%A1',
        'mobile': '%E4%B8%AD%E5%9B%BD%E7%A7%BB%E5%8A%A8',
        'unicom': '%E4%B8%AD%E5%9B%BD%E8%81%94%E9%80%9A'
    }

    payload = {
        "userId": "",
        "password": "",
        "service": "",
        "queryString": "",
        "operatorPwd": "",
        "operatorUserId": "",
        "validcode": "",
        "passwordEncrypt": "false"
    }

    userIndex = {
        'userIndex': ''
    }

    def __init__(self, id, passwd, service='unicom'):
        """
        I like unicom, so the default service is unicom. :P

        :param id: your school userId
        :param passwd: your secret
        :param service: campus telecom mobile unicom
        """
        self.payload['userId'] = id
        self.payload['password'] = passwd
        self.payload['service'] = self.service[service]

    def getOnlineUserInfo(self):
        """
        可以获取到详细的用户信息，包括mac地址和存活时间，但是刚登录成功以后调用这个api需要多请求至少3次才能成功。
        """
        response = requests.post(self.OnlineUserInfo, headers=header, data=self.userIndex)
        print(response.status_code)
        print(response.content.decode('utf-8', 'ignore'))

    def getErrorMsg(self):
        """
        登录成功后调用，正常不会返回任何内容。
        """
        response = requests.post(self.ErrorMsg, headers=header, data=self.userIndex)
        print(response.status_code)
        print(response.content.decode('utf-8', 'ignore'))

    def ifconfig(self):
        """
        如果没有登录的话返回False，已经登录了返回True。
        通过正则表达式提取重定向的url，而这个url刚好包含了queryString，正是登录校园网所必须的关键字段。
        """
        res = requests.get(self.url, headers=header)
        content = res.content.decode('utf-8', 'ignore')
        redirect_url = re.findall(re.compile(r"top.self.location.href='(.*?)'"), content)
        if len(redirect_url) >= 1:
            redirect_url = redirect_url[0]
            self.payload['queryString'] = redirect_url.split('?')[1]
            return False
        else:
            return True

    def connect(self):
        """
        执行登录校园网之前需要先通过ifnoconfig()获取最新的queryString。
        """
        response = requests.post(self.login, headers=header, data=self.payload)
        msg = json.loads(response.content.decode('utf-8', 'ignore'))
        print(response.status_code)
        if msg['result'] == 'success':
            self.userIndex['userIndex'] = msg['userIndex']
            print(self.userIndex)
            logging.warning('网络连接成功')
        elif msg['result'] == 'fail':
            logging.warning('网络连接失败：%s' % msg['message'])
        else:
            logging.error('未知状态：%s' % msg['message'])

    def disconnect(self):
        """
        主动断开校园网的连接。测试时userIndex字段不是必须的。
        """
        response = requests.post(self.logout, headers=header, data=self.userIndex)
        print(response.status_code)
        print(response.content.decode('utf-8', 'ignore'))


parser = argparse.ArgumentParser(description="quickly connect to campus network.")
parser.add_argument("-i", "--id", type=str, help="your school userId")
parser.add_argument("-p", "--password", type=str, help="your password")
parser.add_argument("-s", "--service", type=str, choices=['campus', 'telecom', 'mobile', 'unicom'], default='unicom',
                    help="select the service provider (default: unicom)")
parser.add_argument("-q", "--quit", action="store_true", help="disconnect campus network")
parser.add_argument("-l", "--loop", action="store_true", help="loop check network status and auto connect")
parser.add_argument("-d", "--detail", action="store_true", help="show online user info")
parser.add_argument("-t", "--time", type=int, default=300, help="loop check delay ms (default: 300s)")
args = parser.parse_args()

pi = conn(id=args.id, passwd=args.password, service=args.service)


def start():
    query = pi.ifconfig()
    if not query:
        pi.connect()
    else:
        logging.info('网络已连接')


if args.detail:
    pi.getOnlineUserInfo()

if args.quit:
    pi.disconnect()

if args.loop:
    while True:
        try:
            start()
            time.sleep(args.time)
        except OSError:
            time.sleep(args.time // 2)
        except Exception as error:
            logging.error(error)

else:
    start()
