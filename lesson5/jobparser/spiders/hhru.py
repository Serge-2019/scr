# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    pages = 1
    limit = 10
    allowed_domains = ['hh.ru']
    start_urls = []

    def __init__(self, **kwargs):
        self.limit = kwargs.get('limit', 2)
        query = kwargs.get('query', False)
        if query:
            self.start_urls.append(f'https://hh.ru/search/vacancy?text={query}&area=113&st=searchVacancy')
        super().__init__(**kwargs)

    def parse(self, response: HtmlResponse):
        nextPage = response.xpath('//a[@data-qa="pager-next"]/@href').extract_first()
        if nextPage:
            self.pages += 1
            if self.pages <= self.limit:
                yield response.follow(nextPage, callback=self.parse)

        vacancies = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').extract()
        for link in vacancies:
            yield response.follow(link, self.vacancy_parse)

    def getMeta(self, group, name):
        return f"//span[@itemprop='{group}']//meta[@itemprop='{name}']/@content"

    def vacancy_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=JobparserItem(), response=response)
        loader.add_xpath('name', "//h1[@data-qa='vacancy-title']//text()")
        loader.add_xpath('company', self.getMeta('identifier', 'name'))
        loader.add_xpath('vacancy_id', self.getMeta('identifier', 'value'))
        loader.add_xpath('city', self.getMeta('address', 'addressLocality'))
        loader.add_xpath('region', self.getMeta('address', 'addressRegion'))
        loader.add_xpath('street', self.getMeta('address', 'streetAddress'))
        loader.add_xpath('minSalary', self.getMeta('baseSalary', 'value'))
        loader.add_xpath('minSalary', self.getMeta('baseSalary', 'minValue'))
        loader.add_xpath('maxSalary', self.getMeta('baseSalary', 'maxValue'))
        loader.add_xpath('currency', self.getMeta('baseSalary', 'currency'))
        loader.add_value('url', response.url)
        yield loader.load_item()
