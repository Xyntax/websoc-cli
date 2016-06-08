# !/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
从杂乱文本中提取IP，并自动创建WebSOC扫描任务
代码较粗糙= =!
"""
__author__ = 'cdxy'

import requests
import sys
from extracts import getIP
from bs4 import BeautifulSoup
from config import *

"""
POST /login/ HTTP/1.1
Host: 118.192.48.11:8132
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
DNT: 1
Referer: http://118.192.48.11:8132/login/
Cookie: csrftoken=KWX1b46wfceRa4fJ2MNGpvhXRa935ifm; sessionid=q6s8g27vido7zj60qbrs3bnq2wn37k15
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 96

username=aaaa&password=aaaa&next=%2Fsite%2F&csrfmiddlewaretoken=KWX1b46wfceRa4fJ2MNGpvhXRa935ifm
"""


class auto():
    def __init__(self, name, file, url=config.BASE_URL, usr=config.USER, pwd=config.PASS):
        self.baseURL = url
        self.loginURL = self.baseURL + '/login/'
        self.postURL = self.baseURL + '/api/v3/vgroup/'
        self.usr = usr
        self.pwd = pwd
        self.name = name
        self.tags = 'xy-bot'
        self.target_list = self._get_ips(file)
        print self.target_list
        self.s = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
            'Referer': self.baseURL
        }
        self.run()

    def login(self):
        main_page = self.s.get(self.loginURL)

        data = self._get_static_post_attr(main_page.content)
        data['username'] = self.usr
        data['password'] = self.pwd
        final = self.s.post(self.loginURL, data=data, headers=self.headers)

        if '<div class="modal hide fade" id="modal_add_group">' in final.content:
            print 'Login success'
            return True
        else:
            sys.exit('Login error')

    def _get_ips(self, file):
        str = "["
        for each in getIP(open(file).read(), True, True):
            str += '"http://' + each + '",'
        return str[:-1] + "]"

    def _get_static_post_attr(self, page_content):
        """
        拿到<input type='hidden'>的post参数，并return
        """
        _dict = {}
        soup = BeautifulSoup(page_content, "html.parser")
        for each in soup.find_all('input'):
            if 'value' in each.attrs and 'name' in each.attrs:
                _dict[each['name']] = each['value']
        return _dict

    """
    POST /api/v3/vgroup/ HTTP/1.1
    Host: 118.192.48.11:8132
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0
    Accept: application/json, text/javascript, */*; q=0.01
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    Accept-Encoding: gzip, deflate
    DNT: 1
    Content-Type: application/json
    X-CSRFToken: aZqRebeIdLBuLqttUUVYi7wpvSxQqWDV

    Referer: http://118.192.48.11:8132/task/vgroup_add_edit/
    Content-Length: 1643
    Cookie: csrftoken=aZqRebeIdLBuLqttUUVYi7wpvSxQqWDV; sessionid=63d21roxa8mn3ptmd7ngdgwin1d2qfsp
    Connection: keep-alive

    {"created_at":"2016-06-08T05:06:59.912Z","enabled":true,"stat":null,"site_list":["http://www.baidu.com","http://www.cdxy.me"],"temp":false,"name":"cdxy","tags":["cdxy"],"from_time":null,"to_time":null,"run_at":null,"open_modules":["siteinfo","availability","content","weakness"],"siteinfo":true,"availability":{"enabled":true,"cycle":{"value":30,"unit":0},"priority":6,"spider":{"depth":0,"max_page":"10"},"modules":{"availability":["dns","dns_hijack","ping","http_get","http_get_full_time"]}},"content":{"enabled":true,"cycle":{"value":12,"unit":1},"priority":6,"spider":{"depth":3,"max_page":100},"modules":{"content":{"black_links":{"enabled":true},"malscan":{"enabled":true,"mode":"deep","evidence":false},"keyword":{"enabled":true,"level":3,"sys":true,"evidence":false},"deface":{"enabled":false,"level":3,"evidence":false,"text":3,"image":1,"bin":false,"ignore_authcode":false,"exclude_url":[]},"wad":{"enabled":false}}}},"weakness":{"enabled":true,"cycle":{"value":1,"unit":3},"priority":6,"spider":{"depth":10,"max_page":1000},"modules":{"weakness":{"template_id":"56f51bc443b909240a1d8b79"}}},"advanced_spider":{"spider":{"thread_count":20,"timeout":30,"delay":0,"max_url_param":10,"proxy":null,"referer":null,"ua":null,"gather_scope":1,"include_domains":[],"exclude_domains":[],"include_urls":[],"exclude_urls":[],"auth":null,"pre_login":{"url":null,"params":null},"cookie":null,"parse_webkit":0}},"expert_mode":["expert_cloud","expert_dist404","expert_cookie","expert_referer","expert_ua","expert_uri","expert_webvul_verify","expert_waf","expert_sql_verify","expert_sql_deep","expert_allvul","expert_xss_utf7","expert_adv_malscan"]}

    """

    def addTargets(self):
        print self.target_list
        # 注意时间设置只能向后
        data = '{"created_at":"2017-06-08T06:18:40.433Z","enabled":true,"stat":null,"site_list":' + self.target_list
        data += ',"temp":true,"name":"' + self.name
        data += '","tags":["' + self.tags + '"]'
        data += ',"from_time":null,"to_time":null,"run_at":null,"open_modules":["siteinfo","availability","content","weakness"],"siteinfo":true,"availability":{"enabled":true,"cycle":{"value":30,"unit":0},"priority":6,"spider":{"depth":0,"max_page":"10"},"modules":{"availability":["dns","dns_hijack","ping","http_get","http_get_full_time"]}},"content":{"enabled":true,"cycle":{"value":12,"unit":1},"priority":6,"spider":{"depth":3,"max_page":100},"modules":{"content":{"black_links":{"enabled":true},"malscan":{"enabled":true,"mode":"fast","evidence":false},"keyword":{"enabled":true,"level":3,"sys":true,"evidence":false},"deface":{"enabled":false,"level":3,"evidence":false,"text":3,"image":1,"bin":false,"ignore_authcode":false,"exclude_url":[]},"wad":{"enabled":false}}}},"weakness":{"enabled":true,"cycle":{"value":1,"unit":3},"priority":6,"spider":{"depth":5,"max_page":1000},"modules":{"weakness":{"template_id":"56f51bc443b909240a1d8b79"}}},"advanced_spider":{"spider":{"thread_count":20,"timeout":30,"delay":0,"max_url_param":10,"proxy":null,"referer":null,"ua":null,"gather_scope":1,"include_domains":[],"exclude_domains":[],"include_urls":[],"exclude_urls":[],"auth":null,"pre_login":{"url":null,"params":null},"cookie":null,"parse_webkit":0}},"expert_mode":["expert_cloud","expert_dist404","expert_webvul_verify","expert_waf","expert_sql_verify"],"prelogin":true}'
        # print data
        self.headers['X-CSRFToken'] = self.s.cookies._find('csrftoken')
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.headers['Content-Type'] = 'application/json'
        # print self.headers
        ans = self.s.post(self.postURL, data=data, headers=self.headers).content
        if '{"user_id":,' in ans:
            print 'success'
        else:
            sys.exit(ans)

    def run(self):
        self.login()
        self.addTargets()


if __name__ == '__main__':
    try:
        auto(sys.argv[1], sys.argv[2])
    except IndexError:
        print '从文本中提取url并自动创建websoc扫描任务'
        print 'usage:\n python websoc-cli.py [targetName] [file]\nexample:\n ' \
              'python websoc-cli.py mytask aaa.txt'
