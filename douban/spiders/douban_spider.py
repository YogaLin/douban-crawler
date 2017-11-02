# -*- coding: utf-8 -*-
"""
    crawl douban user

    Yoga Lin | 2017/10/29 10:24
"""

import scrapy
import sys
import re
import random

from douban.items import UserItem
from douban.items import MovieItem

reload(sys)
sys.setdefaultencoding('utf-8')

class DoubanSpiderSpider(scrapy.Spider):
    name = 'douban_spider'
    # start_users_id = ['121253425', 'staymiao', '137816276', 'bibibbbi', '72452043', '5580906', '88584584']
    start_users_id = ['121253425']
    douban_people_tpl = 'https://www.douban.com/people/%s'
    follow_people_tpl = 'https://www.douban.com/people/%s/contacts'
    fans_people_tpl = 'https://www.douban.com/people/%s/rev_contacts'
    collect_movie_tpl = 'https://movie.douban.com/people/%s/collect'
    wish_movie_tpl = 'https://movie.douban.com/people/%s/wish'
    user_set = set(start_users_id)
    user_num_id_re = re.compile(r'u(\d+)-')
    user_id_re = re.compile(r'people\/(\d+)')
    cookies_list = ['ll="118282"; bid=O2x7f2lzhU8; ps=y; ct=y; _ga=GA1.2.621481083.1508593277; ue="838625770@qq.com"; dbcl2="121253425:xPjua9UcOsE"; ap=1; _vwo_uuid_v2=4A5585EC2BAFE6C81B9E1F141AE1E2A5|71c3013b793a4fef395c8b01dbdc328f; ck=RHVT; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1509548345%2C%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F26979545%2Fcreators%22%5D; __utmt=1; _pk_id.100001.8cb4=49f14300be5eca1f.1508593317.12.1509548454.1509467789.; _pk_ses.100001.8cb4=*; push_noty_num=0; push_doumail_num=0; __utma=30149280.621481083.1508593277.1509467277.1509548345.13; __utmb=30149280.8.10.1509548345; __utmc=30149280; __utmz=30149280.1509372080.11.4.utmcsr=baidu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=30149280.12125']
    max_depth = 5

    def get_random_cookies(self):
        """
        get a random cookies in cookies_list
        """
        cookies = random.choice(self.cookies_list)
        #cookies = self.cookies_list[2]
        rt = {}
        for item in cookies.split(';'):
            key, value = item.split('=')[0].strip(), item.split('=')[1].strip()
            rt[key] = value
        return rt

    def start_requests(self):
        """
        以一个用户id拼接成个人中心url，开始爬取
        """
        for user_id in self.start_users_id:
            item = UserItem()
            item['user_id'] = user_id
            item['from_user_id'] = '%s|ROOT' % user_id
            yield scrapy.Request(url = self.douban_people_tpl % user_id, cookies = self.get_random_cookies(), meta = {'item': item}, callback = self.parse_people)

    def parse_people(self, response):
        """
        解析个人中心页面
        """
        depth = 0
        item = response.meta['item']
        item['crawl_depth'] = depth
        head_img = response.xpath('//*[@id="db-usr-profile"]/div[@class="pic"]/a/img/@src').extract()
        item['head_img'] = head_img[0] if head_img else None
        user_name = response.xpath('//*[@id="db-usr-profile"]/div[@class="info"]/h1/text()').extract()
        item['user_name'] = user_name[0].strip() if user_name else None
        user_num_id = self.user_num_id_re.findall(item['head_img'])
        item['user_num_id'] = user_num_id[0] if user_num_id else None
        yield item
        self.user_set.add(item['user_id'])
        self.user_set.add(item['user_num_id'])

        follow_url = self.follow_people_tpl % item['user_id']
        yield scrapy.Request(url = follow_url, cookies = self.get_random_cookies(), meta = {'from_user_id': item['user_id'], 'depth': depth + 1}, callback = self.parse_follow_fan)

        fans_url = self.fans_people_tpl % item['user_id']
        yield scrapy.Request(url = fans_url, cookies = self.get_random_cookies(), meta = {'from_user_id': item['user_id'], 'depth': depth + 1}, callback = self.parse_follow_fan)

        # collect_movie_tpl
        # wish_movie_tpl

    def parse_follow_fan(self, response):
        """
        解析关注的用户页面以及粉丝页面
        """
        from_user_id = response.meta['from_user_id']
        depth = response.meta['depth']
        if response.url.endswith('list'):
            user_list = response.xpath('//*[@id="content"]//ul[@class="user-list"]/li')
            for user in user_list:
                item = UserItem()
                item['crawl_depth'] = depth
                item['from_user_id'] = from_user_id
                user_id = user.xpath('a/@href').extract()
                user_id = self.user_id_re.findall(user_id[0]) if user_id else None
                item['user_id'] = user_id[0] if user_id else None
                user_name = user.xpath('a/@title').extract()
                item['user_name'] = user_name[0] if user_name else None
                head_img = user.xpath('a/img/@src').extract()
                item['head_img'] = head_img[0] if head_img else None
                user_num_id = self.user_num_id_re.findall(item['head_img'])
                item['user_num_id'] = user_num_id[0] if user_num_id else None
                if item['user_id'] == None:
                    item['user_id'] = item['user_num_id']

                if item['user_id'] not in self.user_set and item['user_num_id'] not in self.user_set:
                    yield item
                    self.user_set.add(item['user_id'])
                    self.user_set.add(item['user_num_id'])
                    if depth < self.max_depth:
                        follow_url = self.follow_people_tpl % item['user_id']
                        yield scrapy.Request(url = follow_url, cookies = self.get_random_cookies(), meta = {'from_user_id': item['user_id'], 'depth': depth + 1}, callback = self.parse_follow_fan)

                        fans_url = self.fans_people_tpl % item['user_id']
                        yield scrapy.Request(url = fans_url, cookies = self.get_random_cookies(), meta = {'from_user_id': item['user_id'], 'depth': depth + 1}, callback = self.parse_follow_fan)
        else:
            user_list = response.xpath('//*[@class="obu"]')
            for user in user_list:
                item = UserItem()
                item['crawl_depth'] = depth
                item['from_user_id'] = from_user_id
                user_id = user.xpath('dt/a/@href').extract()
                user_id = self.user_id_re.findall(user_id[0]) if user_id else None
                item['user_id'] = user_id[0] if user_id else None
                user_name = user.xpath('dt/a/img/@alt').extract()
                item['user_name'] = user_name[0] if user_name else None
                head_img = user.xpath('dt/a/img/@src').extract()
                item['head_img'] = head_img[0] if head_img else None
                user_num_id = self.user_num_id_re.findall(item['head_img'])
                item['user_num_id'] = user_num_id[0] if user_num_id else None
                if item['user_id'] == None:
                    item['user_id'] = item['user_num_id']

                if item['user_id'] not in self.user_set and item['user_num_id'] not in self.user_set:
                    yield item
                    self.user_set.add(item['user_id'])
                    self.user_set.add(item['user_num_id'])
                    if depth < self.max_depth:
                        follow_url = self.follow_people_tpl % item['user_id']
                        yield scrapy.Request(url = follow_url, cookies = self.get_random_cookies(), meta = {'from_user_id': item['user_id'], 'depth': depth + 1}, callback = self.parse_follow_fan)

                        fans_url = self.fans_people_tpl % item['user_id']
                        yield scrapy.Request(url = fans_url, cookies = self.get_random_cookies(), meta = {'from_user_id': item['user_id'], 'depth': depth + 1}, callback = self.parse_follow_fan)