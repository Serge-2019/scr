# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    vacancy_id = scrapy.Field()
    company = scrapy.Field()
    city = scrapy.Field()
    region = scrapy.Field()
    street = scrapy.Field()
    minSalary = scrapy.Field()
    maxSalary = scrapy.Field()
    currency = scrapy.Field()
    pass
