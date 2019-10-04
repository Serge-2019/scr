# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class DataBasePipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['avito']

    def process_item(self, item, spider):
        collection = self.db['auto']
        collection.insert_one(item)
        print(item['title'], item['price'])
        return item


class AvitoPhotosPipelines(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except TypeError as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
