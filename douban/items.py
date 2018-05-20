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


class DoubanItem(scrapy.Item):
    """ Collect Fieds needed """
    user_id = scrapy.Field()
    item_type = scrapy.Field()
    item_id = scrapy.Field()
    item_name = scrapy.Field()
    item_other_name = scrapy.Field()
    item_intro = scrapy.Field()
    item_rating = scrapy.Field()
    item_date = scrapy.Field()
    item_tags = scrapy.Field()
    item_comment = scrapy.Field()
    item_poster_id = scrapy.Field()
