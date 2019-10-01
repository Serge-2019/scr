# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SJSpider(scrapy.Spider):
    name = 'superjob'
    pages = 1
    limit = 10
    allowed_domains = ['www.superjob.ru']
    start_urls = []

    def __init__(self, **kwargs):
        self.limit = kwargs.get('limit', 2)
        query = kwargs.get('query', False)
        if query:
            self.start_urls.append(f'https://www.superjob.ru/vacancy/search/?keywords={query}')
        super().__init__(**kwargs)

    def parse(self, response: HtmlResponse):
        nextPage = response.xpath('//a[contains(@class, "f-test-link-dalshe")]/@href').extract_first()
        if nextPage:
            self.pages += 1
            if self.pages <= self.limit:
                yield response.follow(nextPage, callback=self.parse)

        vacancies = response.xpath('////a[contains(@class, "_1QIBo")]/@href').extract()
        for link in vacancies:
            yield response.follow(link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        item = {
            "name": response.xpath("//h1/text()").extract_first(default=None),
            "vacancy_id": re.sub(r'.+-(\d+)\.html$', '\\1', response.url),
            "company": response.xpath("//h2[contains(@class, '_15msI')]/text()").extract_first(default=None),
        }

        if not item['name']:
            return

        s = response.xpath("//span[@class='_3mfro _2Wp8I ZON4b PlM3e _2JVkc']/span/text()").extract()
        a = list(filter(lambda x: x.isdigit(), map(lambda x: re.sub(r'[^\d]', '', x), s)))
        if len(a) > 0:
            item['minSalary'] = a[0]
            item['maxSalary'] = a[1] if len(a) > 1 else a[0]

        a = response.xpath(
            "//span[@class='_6-z9f']/span/span[contains(@class, '_2JVkc')]/text() |"
            "//span[@class='_6-z9f']/span[contains(@class, '_2JVkc')]/text()").extract_first(default=None)
        if a:
            a = a.split(",")
            if len(a) > 0:
                item['city'] = a.pop(0)
                item['street'] = ",".join(map(lambda x: x.strip(), a))

        yield JobparserItem(**item)
