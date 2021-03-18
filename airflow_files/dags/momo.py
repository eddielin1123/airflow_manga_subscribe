from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
import pandas as pd

# headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56'}

key_word = '手機'
page = 1
url_list = []
# while True:
url = 'https://shopee.tw/shop/7421067/search?page=100tBy=pop'

display = Display(visible=0, size=(800, 800))  
display.start()
driver = webdriver.Chrome()
driver.get(url)
retry = 1

item = driver.find_element_by_class_name('_1Sxpvs')
print(item)
    

    # momo
#     try: 
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'goodsUrl')))
#         items = driver.find_elements_by_class_name('goodsUrl')
#     except Exception, TimeoutError:
#         while retry <= 3:
#             print('連線失敗 第{}次重試中'.format(retry))
#             WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'goodsUrl')))
#             retry -= 1
#     if items == []:
#         break
#     else:
#         for i in items:
#             i_url = i.get_attribute("href")
#             url_list.append(i_url)
#             print(i_url)
#     print(url)
#     print('第{}頁結束'.format(page))
#     page += 1

# df = pd.DataFrame({'url':url_list}).to_csv('/home/eddie/momo/momo/spiders/urls.txt', header=True, index=False, sep='\t', mode='a')
driver.quit()
