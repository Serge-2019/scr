# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
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

    def getMeta(self, response, base):
        selectors = response.xpath(f"//span[@itemprop='{base}']//meta")
        meta = {}
        for i in selectors:
            meta[i.attrib['itemprop']] = i.attrib['content']
        return meta

    def vacancy_parse(self, response: HtmlResponse):
        s = self.getMeta(response, 'baseSalary')
        i = self.getMeta(response, 'identifier')
        a = self.getMeta(response, 'address')

        item = {
            "name": "".join(response.xpath("//h1[@data-qa='vacancy-title']//text()").extract()),
            "vacancy_id": i.get('value', '0'),
            "company": i.get('name', ''),
            "city": a.get('addressLocality', ''),
            "region": a.get('addressRegion', ''),
            "street": a.get('streetAddress', ''),
            "minSalary": s.get('minValue', s.get('value', 0)),
            "maxSalary": s.get('maxValue', s.get('minValue', s.get('value', 0))),
            "currency": s.get('currency', 'RUR')
        }

        yield JobparserItem(**item)
