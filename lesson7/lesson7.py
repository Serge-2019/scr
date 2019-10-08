import json
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
    db = client['mvideo']
    db.products.create_index([('productId', ASCENDING)], unique=True)
except Exception as e:
    print('ERROR: не смогли подключиться к базе данных', e)

driver = webdriver.Chrome(executable_path='./chromedriver')
driver.maximize_window()
driver.get('https://www.mvideo.ru/')

ids = []
hits = "(//div[@data-init='gtm-push-products'])[1]"

while True:
    try:
        # waiting for ajax loader disappered
        is_disappeared = WebDriverWait(driver, 30, 1, (ElementNotVisibleException)).until_not(
            lambda x: x.find_element_by_class_name("ajax-overlay").is_displayed())
    except:
        pass

    try:
        products = driver.find_elements_by_xpath(f"{hits}//a[@class='sel-product-tile-title']")
    except Exception as e:
        print('Продукты не найдены:', e)
        break

    for p in products:
        item = json.loads(p.get_attribute('data-product-info'))
        item['productLink'] = p.get_attribute('href')
        if item['productId'] in ids:
            continue
        try:
            db.products.update_one({'productId': item['productId']}, {'$set': item}, upsert=True)
            ids.append(item['productId'])
            print(f'Добавлен/обновлен продукт: {item["productId"]} {item["productName"]}')
        except Exception as e:
            print('Не смогли добавить/обновить товар: ', e)

    try:
        a = driver.find_element_by_xpath(f"{hits}//a[@class='next-btn sel-hits-button-next']")
        a.send_keys(Keys.RETURN)
    except:
        break

print(f'Всего добавлено {len(ids)} продуктов')
driver.quit()
