# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from avitoparser.items import AvitoAuto
from scrapy.loader import ItemLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/rossiya/avtomobili']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        fields = response.xpath("//div[@class='item-view-block']//li/span/text()").getall()
        values = response.xpath("//div[@class='item-view-block']//li/span/following-sibling::text()").getall()

        loader = ItemLoader(item=AvitoAuto(), response=response)
        loader.add_xpath(
            'photos',
            '//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url')
        loader.add_xpath('price', "//span[@itemprop='price'][1]/@content")
        loader.add_xpath('title', "//h1[@class='title-info-title']/span/text()")
        loader.add_xpath('ad_id', "//span[@data-marker='item-view/item-id']/text()")
        loader.add_value('params', zip(fields, values))

        yield loader.load_item()
