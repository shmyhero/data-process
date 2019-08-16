import urllib2
from selenium import webdriver

class HttpHelper:

    def __init__(self):
        pass

    @staticmethod
    def http_get_with_time_out(url, headers=None):
        if headers:
            f = urllib2.urlopen(urllib2.Request(url=url, headers=headers), timeout=10)
        else:
            f = urllib2.urlopen(url, timeout=10)
        s = f.read()
        return s

    @staticmethod
    def http_get(url, headers=None, retry=5):
        for i in range(retry):
            try:
                content = HttpHelper.http_get_with_time_out(url, headers)
                return content
            except Exception:
                pass
        raise Exception('Http request failed for %s times' % retry)

    @staticmethod
    def webdriver_http_get(url, chrome_driver_path):
        driver = webdriver.Chrome(chrome_driver_path)
        driver.get(url)
        content = driver.page_source
        driver.quit()
        return content

