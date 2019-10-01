# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient, ASCENDING


class JobparserPipeline(object):
    def __init__(self, stats):
        client = MongoClient('localhost', 27017)
        self.db = client.vacancies
        self.stats = stats
        pass

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        if spider.name not in self.db.list_collection_names():
            collection.create_index([('vacancy_id', ASCENDING)], unique=True)

        query = {'vacancy_id': item['vacancy_id']}
        try:
            exist = collection.find_one(query)
            collection.update_one(query, {'$set': item}, upsert=True)
            print(spider.name.upper(), end=': ')
            if not exist:
                # collection.insert_one(item)
                print('ADDED:', end=' ')
                self.stats.inc_value('added')
            else:
                print('UPDATED:', end=' ')
                self.stats.inc_value('updated')
            print(item['vacancy_id'], ' - ', item['name'], end=' ')
            if item.get('minSalary', False):
                print('- от', item['minSalary'], end=' ')
            if item.get('city', False):
                print(' - ', item['city'], end=' ')
            print()
        except Exception as e:
            print(f'SKIPPED: {e}')
            self.stats.inc_value('skipped')

        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)
