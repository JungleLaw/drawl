import random
import undetected_chromedriver as uc
import certifi
import os
from selenium.webdriver.common.by import By

# 配置SSL证书路径
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

chrome = uc.Chrome(version_main=135)

chrome.get('https://www.temu.com')
# /html/body//div[contains(@class,'mainContent')]//ul[contains(@class,'splide__list')]/li[contains(@class,'splide__slide')]/div

chrome.implicitly_wait(random.randint(30, 50))

elements = chrome.find_elements(By.XPATH,
                                '/html/body//div[contains(@class,"mainContent")]//ul[contains(@class,"splide__list")]/li[contains(@class,"splide__slide")]/div')
for element in elements:
    print('element', element.get_attribute('outerHTML'))

elements[1].click()
chrome.implicitly_wait(random.randint(10, 20))

price_elements = chrome.find_elements(
    By.XPATH, "/html/body//div[contains(@class,'js-goods-list')]/div[contains(@class,'autoFitList')]//div[contains(@class,'_2myxWHLi')]")
for price_element in price_elements:
    print('price_element', price_element.get_attribute('outerHTML'))
