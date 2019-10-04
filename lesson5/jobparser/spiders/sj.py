# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
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
        loader = ItemLoader(item=JobparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('company', "//h2[contains(@class, '_15msI')]/text()")
        loader.add_xpath('vacancy_id', '//div[@class="_1Tjoc _3ifBO Ghoh2 _3lvIR _3WTx0"]'
                         '//div[@class="_2g1F-"][1]/span[1]/text()')

        loader.add_xpath('street',
                         "//span[@class='_6-z9f']/span/span[contains(@class, '_2JVkc')]/text() |"
                         "//span[@class='_6-z9f']/span[contains(@class, '_2JVkc')]/text()"
                         )

        loader.add_xpath('minSalary', "//span[@class='_3mfro _2Wp8I ZON4b PlM3e _2JVkc']"
                         "/span[1]/text()")
        loader.add_xpath('maxSalary', "//span[@class='_3mfro _2Wp8I ZON4b PlM3e _2JVkc']"
                         "/span[3]/text()")
        loader.add_value('url', response.url)
        yield loader.load_item()
