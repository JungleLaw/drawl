import random
import undetected_chromedriver as uc
import certifi
import os
import logging
from selenium.webdriver.common.by import By
from scrapy.http import HtmlResponse
import json

logger = logging.getLogger(__name__)


# 配置SSL证书路径
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

chrome = uc.Chrome(version_main=135)

chrome.get('file:///Users/law/Hub/python/drawl/tmc/tmc/spiders/response_body_%E5%AE%B6%E5%B1%85%E5%8E%A8%E6%88%BF%E7%94%A8%E5%93%81%20-%20%E4%BB%8E%20Temu%20%E5%8F%91%E8%B4%A7%E7%9A%84%E5%95%86%E5%93%81%E5%85%8D%E8%BF%90%E8%B4%B9.html')
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

# temu_data = None
# # Load the JSON file
# with open("./temu.json", "r") as file:
#     temu_data = json.load(file)

# body = chrome.page_source
# current_url = chrome.current_url  # URL 可能已改变 (例如重定向后)
# logger.info(f"Page source retrieved. Current URL: {current_url}")
# response = HtmlResponse(
#                     url=current_url,
#                     body=body,
#                     encoding='utf-8',
#                 )
# goods_list_item_elements = response.xpath(temu_data['home_elements']['goods_list_item'])
# logger.info(f"Goods list item elements found: {len(goods_list_item_elements)}")
