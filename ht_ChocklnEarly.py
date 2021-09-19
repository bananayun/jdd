# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/12
# @Author  : 2984922017@qq.com
# @File    : ChockInEarly.py
# @Software: PyCharm

'''
cron:  35 0,19 * * * ChockInEarly.py
new Env('欢太早睡打卡');
'''

import os
import sys
import time
import json
import random
import logging

# 日志模块
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logFormat = logging.Formatter("%(message)s")

# 日志输出流
stream = logging.StreamHandler()
stream.setFormatter(logFormat)
logger.addHandler(stream)

# 日志录入时间
logger.info(f"任务:{'任务中心'}\n时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")

# 第三方库
try:
    import requests
except ModuleNotFoundError:
    print("缺少requests依赖！程序将尝试安装依赖！")
    os.system("pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple")
    os.execl(sys.executable, 'python3', __file__, *sys.argv)

class CheckInEarly:
    def __init__(self,dic):
        self.dic = dic
        self.sess = requests.session()

    # 登录验证
    def login(self):
        url = 'https://store.oppo.com/cn/oapi/users/web/member/check'
        headers = {
            'Host': 'store.oppo.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        response = self.sess.get(url=url,headers=headers).json()
        if response['code'] == 200:
            logger.info(f"{self.dic['user']}\t登录成功")
            return True
        else:
            logger.info(f"{self.dic['user']}\t登录失败")
            return False

    # 报名或打卡
    # 报名或打卡是同一个链接，配合Linux定时系统
    def early(self):
        url = 'https://store.oppo.com/cn/oapi/credits/web/clockin/applyOrClockIn'
        headers = {'Host': 'store.oppo.com',
                   'Connection': 'keep-alive',
                   'source_type': '501',
                   'clientPackage': 'com.oppo.store',
                   'Accept': 'application/json, text/plain, */*',
                   'Referer': 'https://store.oppo.com/cn/app/cardingActivities?us=gerenzhongxin&um=hudongleyuan&uc=zaoshuidaka',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
                   }
        response = self.sess.get(url=url,headers=headers).json()
        if response['code'] == 200:
            if response['data']['clockInStatus'] == 0:
                if response['data']['applyStatus'] == 0:
                    logger.info(f"{self.dic['user']}\t积分过少，取消报名!")
                elif response['data']['applyStatus'] == 1:
                    logger.info(f"{self.dic['user']}\t报名成功!")
                elif response['data']['applyStatus'] == 2:
                    logger.info(f"{self.dic['user']}\t已报名!")
            elif response['data']['clockInStatus'] == 1:
                logger.info(f"{self.dic['user']}\t早睡瓜分积分，打卡成功!")
            elif response['data']['clockInStatus'] == 2:
                logger.info(f"{self.dic['user']}\t早睡瓜分积分,已成功打卡!")
        elif response['code'] == 1000005:
            logger.info(f"{self.dic['user']}\t{response['errorMessage']}")

    # 执行欢太商城实例对象
    def start(self):
        self.sess.headers.update({
            "User-Agent":self.dic['UA']
        })
        self.sess.cookies.update({
            "Cookie":self.dic['CK']
        })
        if self.login() == True:
            self.early()
        logger.info('*' * 40 + '\n')

# 格式化设备信息Json
# 由于青龙的特殊性,把CK中的 app_param 转换未非正常格式，故需要此函数
def transform(string):
    dic2 = {}
    dic1 = eval(string)
    for i in dic1['app_param'][1:-1].split(','):
        dic2[i.split(':')[0]] = i.split(':')[-1]
    dic1['CK'] = dic1['CK'] + f";app_param={json.dumps(dic2,ensure_ascii=False)}"
    return dic1

# 读取青龙CK
def getEnv(key):
    lists = []
    logger.info("尝试导入青龙面板CK...")
    variable = os.environ.get(key)
    if (variable == '') or (variable == None):
        logger.info("青龙面板环境变量 TH_COOKIE 不存在！")
    else:
        for each in variable.split('&'):
            lists.append(transform(each))
    return lists

if __name__ == '__main__':
    for each in getEnv('HT_COOKIE'):
        if each['CK'] != "" and each['UA'] != "":
            checkInEarly = CheckInEarly(each)
            for count in range(3):
                try:
                    time.sleep(random.randint(2,5))    # 随机延时
                    checkInEarly.start()
                    break
                except requests.exceptions.ConnectionError:
                    logger.info(f"{checkInEarly.dic['user']}\t请求失败，随机延迟后再次访问")
                    time.sleep(random.randint(2,5))
                    continue
            else:
                logger.info(f"账号: {checkInEarly.dic['user']}\n状态: 取消登录\n原因: 多次登录失败")
                break
