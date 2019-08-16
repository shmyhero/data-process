from utils.httphelper import HttpHelper
from common.configmgr import ConfigMgr
from selenium import webdriver
from ingestion.yahooscraper import YahooScraper

# print(YahooScraper.get_crumble_and_cookie2())
url = 'https://finance.yahoo.com/quote/SPY'
chrome_driver_path = ConfigMgr.get_others_config()['chromedriver']
print(chrome_driver_path)
driver = webdriver.Chrome(chrome_driver_path)
driver.get(url)
content = driver.page_source
driver.quit()

# content = HttpHelper.webdriver_http_get(url, chrome_driver_path)
print(content)