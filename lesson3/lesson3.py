import requests
import re

from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError

from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup as bs


try:
    client = MongoClient('localhost', 27017)
    db = client['vacancies']
    db.jobs.create_index([('id', ASCENDING)], unique=True)
except Exception as e:
    print('ERROR: не смогли подключиться к базе данных', e)


def insertItems(items):
    try:
        r = db.jobs.insert_many(items, ordered=False)
        cnt = len(r.inserted_ids)
    except BulkWriteError as e:
        cnt = e.details['nInserted']
    finally:
        return cnt


def search(salary):
    query = {'$or': [
        {'salaryMin': {'$gt': salary}},
        {'salaryMax': {'$gt': salary}},
    ]}
    cnt = db.jobs.count_documents(query)
    if not cnt:
        print(f'Не найдено вакансий с зарплатой больше чем {salary}')
        return

    print(f'Найдено {cnt} вакансий:')
    r = db.jobs.find(query)


class Jobs(object):
    url = False
    foundpages = 0
    total = 0

    def log(self, message='ok', end=True):
        print(message, end=' ... ' if not end else '\n')

    def __init__(self, query, pages=2, fromPage=1):
        self.query = query
        self.pages = pages
        self.fromPage = fromPage
        self.run()

    def request(self, page=False):
        url = self.getLink(page)
        headers = {
            'Cache-Control': 'no-cache', 'Connection': 'keep-alive',
            'Referer': 'https://google.com',
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 \
                Safari/537.36'}
        r = requests.get(url, headers=headers)
        if r.ok:
            if not self.url:
                self.url = r.url
            content = bs(r.text, 'html.parser')
            sleep(0.5)
            return content
        else:
            r.raise_for_status()

    def getLink(self, page=False):
        return ''

    def getTotalPages(self, dom):
        return 0

    def getItems(self, dom):
        return []

    def getItem(self, dom):
        return {
            "class": self.__class__.__name__,
            "date": datetime.utcnow()
        }

    def run(self):
        self.log('='*20 + f' {self.__class__.__name__} ' + '='*20)
        self.log(' Запрашиваем главную страницу', False)

        content = self.request()
        self.foundpages = self.getTotalPages(content)
        self.log(f'всего найдено {self.foundpages} страниц')

        if self.fromPage > self.foundpages:
            self.log(f'Начальная страница {self.fromPage} '
                     'больше чем найдено страниц')
            return

        if self.fromPage > 1:
            content = self.request(self.fromPage)

        page = self.fromPage
        pages = min(self.foundpages, self.pages)
        while page <= pages:
            self.log(f'  > парсим вакансии на странице {page}', False)

            items = []
            for i in self.getItems(content):
                item = self.getItem(i)
                if item:
                    items.append(item)

            found = len(items)
            self.log(f'найдено {found} вакансий', False)

            if found:
                cnt = insertItems(items)
                self.total += cnt
                self.log(f'добавлено {cnt}, пропущено {found - cnt} вакансий')
            else:
                self.log('done')

            page += 1
            if page <= pages:
                content = self.request(page)

        self.log(
            f' Обработано {pages} страниц(ы)'
            f' всего добавлено {self.total} вакансий')


class SuperJobs(Jobs):
    def getTotalPages(self, dom):
        try:
            a = dom.find(
                'div', {'class': 'L1p51'}).findChildren(
                'a', recursive=False)
        except:
            return 0

        a.reverse()
        for i in a:
            if i.text.isdigit():
                return int(i.text)

    def getItem(self, dom):
        item = super().getItem(dom)

        try:
            b = dom.find('div', {'class': '_2g1F-'}) \
                .find('div', {'class': '_3syPg _1_bQo _2FJA4'})

            t = b.find('a', {'class': '_1QIBo'})
            item['title'] = t.text
            item['link'] = 'https://www.superjob.ru' + t['href']
            item['id'] = item['class'] + '-' + \
                re.sub(r'.+-(\d+)\.html$', '\\1', item['link'])
        except Exception as e:
            self.log(f' >>>> ERROR: {e}')
            return False

        try:
            item['company'] = b.find('a', {'class': '_205Zx'}).text
            t = b.find('span',
                       {'class': 'f-test-text-company-item-location'}) \
                .findAll('span')
            a = (",".join(map(lambda x: x.text.strip(), t[1:]))).split(',')
            item['location'] = list(set(filter(lambda x: len(x) > 0, map(
                lambda x: re.sub(r'(и ещё )?\d+ станци.', '', x).strip(), a))))
        except:
            pass

        try:
            t = b.find(
                'span', {'class': 'f-test-text-company-item-salary'}).text
            a = re.sub(r'[^\d—]', '', t).split('—')
            if a[0].isdigit():
                item['salaryMin'] = int(a[0])
            if len(a) > 1 and a[1].isdigit():
                item['salaryMax'] = int(a[1])
        except:
            pass

        return item

    def getItems(self, dom):
        try:
            return dom.findAll('div', {'class': 'f-test-vacancy-item'})
        except:
            return []

    def getLink(self, page=False):
        s = f'https://www.superjob.ru/vacancy/search/?keywords={self.query}' \
            if not self.url else self.url
        if page:
            s += f'&page={page}'
        return s


class HHRU(Jobs):
    endpoint = 'https://hh.ru/search/vacancy?L_is_autosearch=false' + \
        '&area=1&clusters=true&enable_snippets=true&'

    def getTotalPages(self, dom):
        try:
            a = dom.findAll('span', {'class': 'pager-item-not-in-short-range'})
            p = int(a[len(a)-1].find('a').text)
            return p
        except:
            return 0

    def getItem(self, dom):
        item = [None] * 6 + ['HH.RU']

        try:
            t = dom.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            item[0] = t.text.strip()
            item[3] = self.endpoint + t['href']
        except:
            return False

        try:
            item[4] = dom.find(
                'a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text\
                .strip()
            t = dom.find('span',
                         {'data-qa': 'vacancy-serp__vacancy-address'})
            item[5] = re.sub(r'и еще \d+', '', t.text).strip()
        except:
            pass

        try:
            t = dom.find('div', {'class': 'vacancy-serp-item__compensation'})
            a = re.sub(r'[^\d-]', '', t.text).split('-')
            if a[0].isdigit():
                item[1] = int(a[0])
            if len(a) > 1 and a[1].isdigit():
                item[2] = int(a[1])
        except:
            pass

        return item

    def getItems(self, dom):
        items = []
        try:
            a = dom.findAll('div', {'class': 'vacancy-serp-item'})
        except:
            return []

        for i in a:
            item = self.getItem(i)
            if item:
                items.append(item)

        return items

    def getLink(self, page=False):
        s = f'text={self.query}'
        if page:
            s += f'&page={page-1}'
        return s


while True:
    print('\nМеню:')
    print(' 1 - Парсинг вакансий в БД')
    print(' 2 - Поиск вакансий по зарплате')
    print(' 3 - Очистить БД')
    print(' [enter] - Выход')
    try:
        i = int(input('Сделайте выбор : ') or 0)
    except:
        continue
    finally:
        print()

    if not i:
        break

    if i == 1:
        vacancy = input('Введите вакансию: ')
        if not vacancy:
            continue
        pages = int(input('Введите кол-во страниц [2]: ') or 2)
        fromPage = int(input('Начиная с страницы [1]: ') or 1)
        sj = SuperJobs(vacancy, pages, fromPage)
        hh = HHRU(vacancy, pages, fromPage)

    if i == 2:
        try:
            salary = int(input('Введите зарплату: '))
        except:
            print('неверный ввод')
        else:
            search(salary)

    if i == 3:
        x = db.jobs.delete_many({})
        print(f'удалено {x.deleted_count} вакансий')
