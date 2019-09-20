import requests
import re
from pprint import pprint
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup as bs


class Jobs(object):
    endpoint = 'https://google.com'
    foundpages = 0
    total = 0
    data = []

    def log(self, message='ok', end=True):
        print(message, end=' ... ' if not end else '\n')

    def __init__(self, query, pages=2):
        self.query = query
        self.pages = pages
        self.run()

    def request(self, page=False):
        headers = {
            'Cache-Control': 'no-cache', 'Connection': 'keep-alive',
            'Referer': self.endpoint,
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 \
                Safari/537.36'}
        url = self.endpoint + self.getLink(page)
        r = requests.get(url, headers=headers)
        if r.ok:
            content = bs(r.text, 'html.parser')
            return content
        else:
            r.raise_for_status()

    def getLink(self, page=False):
        return ''

    def getTotalPages(self, dom):
        return 0

    def getItems(self, dom):
        return []

    def run(self):
        self.log(' Запрашиваем главную страницу', False)
        content = self.request()
        self.foundpages = self.getTotalPages(content)
        self.log(f'найдено {self.foundpages} страниц')

        page = 1
        pages = min(self.foundpages, self.pages)
        while page <= pages:
            self.log(f'  > парсим вакансии на странице {page}', False)
            items = self.getItems(content)
            cnt = len(items)
            self.log(f'получено {cnt} вакансий')
            self.data += items
            self.total += cnt
            page += 1
            sleep(1)
            content = self.request(page)

        self.log(f' Обработано {pages} страниц(ы) ' +
                 f'получено {self.total} вакансий', True)


class SuperJobs(Jobs):
    endpoint = 'https://www.superjob.ru'

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
        item = [None] * 6 + ['SuperJobs']

        try:
            b = dom.find('div', {'class': '_2g1F-'}) \
                .find('div', {'class': '_3syPg _1_bQo _2FJA4'})

            t = b.find('a', {'class': '_1QIBo'})
            item[0] = t.text
            item[3] = self.endpoint + t['href']
        except:
            return False

        try:
            item[4] = b.find('a', {'class': '_205Zx'}).text
            t = b.find('span',
                       {'class': 'f-test-text-company-item-location'}) \
                .findAll('span')
            a = (",".join(map(lambda x: x.text.strip(), t[1:]))).split(',')
            a = list(set(filter(lambda x: len(x) > 0, map(
                lambda x: re.sub(r'(и ещё )?\d+ станци.', '', x).strip(), a))))
            item[5] = ", ".join(a)
        except:
            pass

        try:
            t = b.find(
                'span', {'class': 'f-test-text-company-item-salary'}).text
            a = re.sub(r'[^\d—]', '', t).split('—')
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
            a = dom.findAll('div', {'class': 'f-test-vacancy-item'})
        except:
            return []

        for i in a:
            item = self.getItem(i)
            if item:
                items.append(item)

        return items

    def getLink(self, page=False):
        s = f'/vacancy/search/?keywords={self.query}'
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


vacancy = input('Введите вакансию:')
pages = int(input('Введите кол-во страниц:'))
print()

print('=== Парсинг данных с сайта SuperJobs === ')
sj = SuperJobs(vacancy, pages)

print('\n=== Парсинг данных с сайта HH.ru === ')
hh = HHRU(vacancy, pages)

print(f'\n Сохраняем {sj.total+hh.total} вакансий в result.csv')
print('Анализ данных смотреть в lesson2.ipynb')

columns = [
    'Наименование вакансии',
    'Зарплата MIN',
    'Зарплата MAX',
    'Ссылка на вакансию',
    'Работодатель',
    'Расположение',
    'Сайт'
]

df = pd.DataFrame(sj.data + hh.data, columns=columns)
df.to_csv('result.csv')
print(df.head())
