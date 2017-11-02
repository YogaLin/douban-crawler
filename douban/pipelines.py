# -*- coding: utf-8 -*-
"""
    export users, movies to different file

    Yoga Lin | 2017/10/29 11:08
"""

from scrapy.exporters import CsvItemExporter

class DoubanPipeline(object):
    item_types = ['user', 'movie']

    def get_item_name(self, item):
        """ convert 'UserItem' from to 'user' """
        return type(item).__name__.replace('Item', '').lower()

    def open_spider(self, spider):
        CSV_DIR = spider.settings.get('CSV_DIR')
        self.files = dict([ (name, open(CSV_DIR + name + '.csv', 'w+b')) for name in self.item_types ])
        self.exporters = dict([ (name, CsvItemExporter(self.files[name])) for name in self.item_types ])
        [e.start_exporting() for e in self.exporters.values()]

    def close_spider(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        item_name = self.get_item_name(item)
        if item_name in set(self.item_types):
            self.exporters[item_name].export_item(item)
        return item