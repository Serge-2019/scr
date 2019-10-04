# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

MAPPARAMS = {
    'Год выпуска': 'year',
    'Количество дверей': 'doors',
    'Комплектация': 'equipment',
    'Коробка передач': 'transmission',
    'Марка': 'make',
    'Модель': 'model',
    'Модификация': 'modification',
    'Поколение': 'generation',
    'Привод': 'drive',
    'Пробег': 'mileage',
    'Состояние': 'status',
    'Тип двигателя': 'engineType',
    'Тип кузова': 'body',
    'Цвет': 'color'
}


def cleaner_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values


def to_int(value):
    value = re.sub(r'\D+', '', value)
    try:
        return int(value)
    except:
        return None


class ZipToDict(object):
    def __call__(self, values):
        d = {}
        for param in values:
            f, v = param
            f = re.sub(r'\:$', '', f.strip())
            if f in MAPPARAMS:
                d[MAPPARAMS[f]] = v.strip()
        return d


class AvitoAuto(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(to_int), output_processor=TakeFirst())
    ad_id = scrapy.Field(input_processor=MapCompose(to_int), output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    params = scrapy.Field(input_processor=ZipToDict(), output_processor=TakeFirst())
