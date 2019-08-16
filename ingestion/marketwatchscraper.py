from utils.httphelper import HttpHelper
from utils.stringhelper import string_fetch


class MarketWatchScraper():

    @staticmethod
    def get_data_by_symbol(symbol):
        url = 'https://www.marketwatch.com/investing/fund/%s' % symbol
        # url = 'http://www.marketwatch.com'
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        headers = {
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
            "Connection": "keep-alive"
        }
        content = HttpHelper.http_get(url, headers)
        content = string_fetch(content, 'mw-rangeBar precision=', 'Day Low')
        value = string_fetch(content, '\"last-value\">', '</span>')
        return float(value.replace(',', ''))

if __name__ == '__main__':
    print MarketWatchScraper.get_data_by_symbol('SPY')