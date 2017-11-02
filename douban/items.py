# -*- coding: utf-8 -*-

import scrapy

class UserItem(scrapy.Item):
    """ User Fields needed """
    user_id = scrapy.Field()
    user_num_id = scrapy.Field()
    from_user_id = scrapy.Field() 
    head_img = scrapy.Field()
    # signature = scrapy.Field()
    user_name = scrapy.Field()
    crawl_depth = scrapy.Field()

class MovieItem(scrapy.Item):
    """ Movie Fields needed """
    movie_id = scrapy.Field()
    tags = scrapy.Field()
    score = scrapy.Field()
    name = scrapy.Field()
