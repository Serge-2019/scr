# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join


def to_int(value):
    value = re.sub(r'\D+', '', value)
    try:
        return int(value)
    except:
        return None


def strip(value):
    return re.sub(r'\s+', ' ', value).strip()


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=Join()
    )
    vacancy_id = scrapy.Field(input_processor=MapCompose(to_int), output_processor=TakeFirst())
    company = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    city = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    region = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    street = scrapy.Field(
        input_processor=MapCompose(strip),
        output_processor=TakeFirst()
    )
    minSalary = scrapy.Field(
        input_processor=MapCompose(to_int),
        output_processor=TakeFirst()
    )
    maxSalary = scrapy.Field(
        input_processor=MapCompose(to_int),
        output_processor=TakeFirst()
    )
    currency = scrapy.Field(output_processor=TakeFirst())
