from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sj import SJSpider


def report(crawler, name: str):
    s = crawler.stats.get_stats()
    parsed = s.get('item_scraped_count', 0)
    added = s.get('added', 0)
    skipped = s.get('skipped', 0)
    updated = s.get('updated', 0)
    print(f'{name.upper()}: найдено {parsed}, добавлено {added}, обновлено {updated}, пропущено {skipped}')


if __name__ == '__main__':
    LIMIT = 2
    QUERY = 'PHP Developer'

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)

    HHCrawler = process.create_crawler(HhruSpider)
    SJCrawler = process.create_crawler(SJSpider)

    process.crawl(SJCrawler, limit=LIMIT, query=QUERY)
    process.crawl(HHCrawler, limit=LIMIT, query=QUERY)
    process.start()

    report(HHCrawler, 'hh.ru')
    report(SJCrawler, 'superjob.ru')
