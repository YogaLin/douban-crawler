#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Yoga Lin
# * Email         : lsyoga@foxmail.com
# * Create time   : 2018-05-21 00:07
# * Last modified : 2018-05-21 00:07
# * Filename      : douban.py
# * Description   : Crawl data of given douban collect page
# **********************************************************

import scrapy
import sys
import re
import random

# from douban.items import UserItem
from douban.items import DoubanItem

reload(sys)
sys.setdefaultencoding('utf-8')

class CollectSpider(scrapy.Spider):
    name = 'collect_spider'
    user_ids = [121253425]
    crawl_types = ['collect_movie']

    douban_types = ['collect_movie', 'wise_movie', 'do_movie', 'collect_book', 'wish_book', 'do_book']
    # 看过的电影、想看的电影、在看的电影 url templates
    collect_movie_tpl = 'https://movie.douban.com/people/{}/collect?start={}'
    wish_movie_tpl = 'https://movie.douban.com/people/{}/wish?start={}'
    do_movie_tpl = 'https://movie.douban.com/people/{}/do?start={}'
    # 书籍 url templates
    collect_book_tpl = 'https://book.douban.com/people/{}/collect?start={}'
    wish_book_tpl = 'https://book.douban.com/people/{}/wish?start={}'
    do_book_tpl = 'https://book.douban.com/people/{}/do?start={}'
    douban_url_templates = {
        'collect_movie': collect_movie_tpl,
        'wish_movie': wish_movie_tpl,
        'do_movie': do_movie_tpl,
        'collect_book': collect_book_tpl,
        'wish_book': wish_book_tpl,
        'do_book': do_book_tpl
    }

    cookies_list = []


    def get_random_cookies(self):
        """
        get a random cookies in cookies_list
        """
        cookies = random.choice(self.cookies_list)
        rt = {}
        for item in cookies.split(';'):
            key, value = item.split('=')[0].strip(), item.split('=')[1].strip()
            rt[key] = value
        return rt


    def start_requests(self):
        """
        entry of this spider
        """
        for user_id in self.user_ids:
            for douban_type in self.douban_types:
                if douban_type in self.crawl_types:
                    url_template = self.douban_url_templates[douban_type]
                    if url_template:
                        request_url = url_template.format(user_id, 0) + '&'
                    else:
                        raise Exception('Wrong douban_type: %s' % douban_type)
                    meta = {
                        'url_template': url_template,
                        'douban_type': douban_type,
                        'user_id': user_id
                    }
                    yield scrapy.Request(url=request_url, meta=meta, callback=self.parse_first_page)

    
    def parse_first_page(self, response):
        """
        parse first page to get total pages and generate more requests
        """
        meta = response.meta
        total_page = response.xpath('//*[@id="content"]//div[@class="paginator"]/a[last()]/text()').extract()
        total_page = int(total_page[0]) if total_page else 1
        for page in range(total_page):
            request_url = meta['url_template'].format(meta['user_id'], 15 * page)
            yield scrapy.Request(url=request_url, meta=meta, callback=self.parse_content)
    

    def parse_content(self, response):
        """
        parse collect item of response
        """
        meta = response.meta
        item_list = response.xpath('//*[@id="content"]//div[@class="grid-view"]/div')
        for item in item_list:
            douban_item = DoubanItem()
            douban_item['item_type'] = meta['douban_type']
            douban_item['user_id'] = meta['user_id']
            item_id = item.xpath('div[@class="info"]/ul/li[@class="title"]/a/@href').extract()
            douban_item['item_id'] = int(item_id[0].split('/')[-2]) if item_id else None
            item_name = item.xpath('div[@class="info"]/ul/li[@class="title"]/a/em/text()').extract()
            douban_item['item_name'] = item_name[0].strip() if item_name else None
            item_other_name = item.xpath('div[@class="info"]/ul/li[@class="title"]/a').xpath('string(.)').extract()
            douban_item['item_other_name'] = item_other_name[0].replace(douban_item['item_name'], '').strip() if item_other_name else None
            item_intro = item.xpath('div[@class="info"]/ul/li[@class="intro"]/text()').extract()
            douban_item['item_intro'] = item_intro[0].strip() if item_intro else None
            item_rating = item.xpath('div[@class="info"]/ul/li[3]/*[starts-with(@class, "rating")]/@class').extract()
            douban_item['item_rating'] = int(item_rating[0][6]) if item_rating else None
            item_date = item.xpath('div[@class="info"]/ul/li[3]/*[@class="date"]/text()').extract()
            douban_item['item_date'] = item_date[0] if item_date else None
            item_tags = item.xpath('div[@class="info"]/ul/li[3]/*[@class="tags"]/text()').extract()
            douban_item['item_tags'] = item_tags[0].replace(u'标签: ', '') if item_tags else None
            item_comment = item.xpath('div[@class="info"]/ul/li[4]/*[@class="comment"]/text()').extract()
            douban_item['item_comment'] = item_comment[0] if item_comment else None
            item_poster_id = item.xpath('div[@class="pic"]/a[1]/img[1]/@src').extract()
            douban_item['item_poster_id'] = int(item_poster_id[0].split('/')[-1].split('.')[0][1:]) if item_poster_id else None
            yield douban_item

