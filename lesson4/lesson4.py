import re
import requests
from datetime import datetime
from lxml import html


def getNews(url, xp):
    headers = {
        'Cache-Control': 'no-cache', 'Connection': 'keep-alive',
        'Referer': url,
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 \
            Safari/537.36'}
    r = requests.get(url, headers=headers)
    if r.ok:
        root = html.fromstring(r.text)
    else:
        r.raise_for_status()
        return []

    news = root.xpath(f"{xp}/text()")
    if len(news):
        links = map(
            lambda x: re.sub(r'^\/', url, x),
            root.xpath(f"{xp}/@href"))
        times = root.xpath(f"{xp}/time/text()")
        if not len(times):
            times = [datetime.now().strftime('%H:%M')] * len(news)

    for i in zip(news, links, times):
        print(f'{i[2]:10} | {i[0]:100.100} | {i[1]}')


print('Новости Mail.RU:')
print('-' * 200)
getNews("https://mail.ru/",
        "//div[contains(@class, 'news-item')]//a[not(@class)]")

print('\nНовости Lenta.RU:')
print('-' * 200)

lenta = getNews("https://lenta.ru/",
                "//section[contains(@class, 'b-top7-for-main')]"
                "//div[contains(@class,'item')]//a[time]")
