import re
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotVisibleException
from pymongo import MongoClient, ASCENDING

try:
    client = MongoClient('localhost', 27017)
    db = client['mail']
    db.mails.create_index([('id', ASCENDING)], unique=True)
except Exception as e:
    print('ERROR: не смогли подключиться к базе данных', e)

driver = webdriver.Chrome(executable_path='./chromedriver')
driver.maximize_window()
driver.get('https://account.mail.ru/login/')


def login(username, password):
    try:
        a = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="Login"]'))
        )
        a.clear()
        a.send_keys(username)
        a.submit()

        b = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@data-test-id="submit-button"]'))
        )

        a = driver.find_element_by_xpath('//input[@name="Password"]')
        a.send_keys(password)
        a.submit()

        c = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="/messages/inbox/"]'))
        )

        return True
    except Exception as e:
        print("ERROR:", e)
        return False


def getMails():
    mails = []
    try:
        a = driver.find_elements_by_xpath('//a[contains(@class, "b-datalist__item__link")]')
        for i in a:
            l = i.get_attribute('href')
            t = i.get_attribute('title')
            s = i.get_attribute('data-subject')
            mails.append((l, t, s))
    except:
        pass
    return mails


def getItem(link):
    driver.get(link)
    r = re.match(r'.+thread\/\d\:(.+)\:\d\/', link)
    if not r:
        return False
    idm = r.group(1)

    try:
        subj = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'b-letter__head__subj__text'))
        )

        frm = driver.find_element_by_xpath(
            '//div[@data-mnemo="from"]/span[contains(@class, "b-contact-informer-target")]')
        dt = driver.find_element_by_xpath('//div[@class="b-letter__head__date"]')
        bd = driver.find_element_by_xpath('//div[contains(@class, "b-letter__body__wrap")]')
        html = bd.get_attribute('innerHTML').strip()
        text = re.sub(r'\n+', '\n', bs(html, "html.parser").get_text()).strip()

        item = {
            'id': idm,
            'from_name': frm.get_attribute('data-contact-informer-name'),
            'from_email': frm.get_attribute('data-contact-informer-email'),
            'date': dt.text,
            'subject': subj.text,
            'bodyHtml': html,
            'bodyText': text,
        }
        return item
    except Exception as e:
        print(f'Не удалось загрузить письмо', e)
        return False


if not login('email@mail.ru', 'password'):
    print("Не возможно пройти логин или загрузить входящие")
    driver.quit()
    exit()

mails = getMails()
if not len(mails):
    print("В ящике нет писем")
    driver.quit()
    exit()

for l, t, s in mails:
    print(f'Получаем контент для - {t}: {s}', end='...')
    item = getItem(l)
    if item:
        db.mails.update_one({'id': item['id']}, {'$set': item}, upsert=True)
        print('done')

print(f'Обработано {len(mails)} писем')
driver.quit()
