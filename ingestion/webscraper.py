import json
import traceback
from abc import ABCMeta, abstractmethod
from datetime import datetime
from utils.httphelper import HttpHelper
from utils.stringhelper import string_fetch
from common.symbols import Symbols


class WebScraper(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_current_data(self, symbol):
        pass


class YahooScraper(WebScraper):

    def get_current_data(self, symbol):
        yahoo_symbol = Symbols.get_mapped_symbol(symbol)
        url = 'https://finance.yahoo.com/quote/%s/'% yahoo_symbol
        content = HttpHelper.http_get(url)
        try:
            sub_content = string_fetch(content, 'Currency in USD', 'At close:')
            sub_content = string_fetch(sub_content, 'react-text', 'react-text')
            value = string_fetch(sub_content, '-->', '<!--')
            return float(value.replace(',', ''))
        except Exception:
            sub_content = string_fetch(content, '\"close\":', ',')
            value = round(float(sub_content), 2)
            return value


class MarketWatchScraper(WebScraper):

    def get_current_data(self, symbol):
        url = 'https://www.marketwatch.com/investing/fund/%s' % symbol
        content = HttpHelper.http_get(url)
        content = string_fetch(content, 'mw-rangeBar precision=', 'Day Low')
        value = string_fetch(content, '\"last-value\">', '</span>')
        return float(value.replace(',', ''))


class CNBCScraper(WebScraper):

    def get_current_data(self, symbol):
        url = 'https://www.cnbc.com/quotes/?symbol=%s' % symbol
        content = HttpHelper.http_get(url)
        value = string_fetch(content, '\"previous_day_closing\":\"', '\"')
        return float(value.replace(',', ''))


class SINAScraper(WebScraper):

    def get_current_data(self, symbol):
        url = 'http://hq.sinajs.cn/?list=gb_%s' % symbol.replace('.', '$').lower()
        content = HttpHelper.http_get(url)
        value = string_fetch(content, ',', ',')
        return float(value)


class LaoHu8Scraper(WebScraper):

    def get_current_data(self, symbol):
        url = 'https://www.laohu8.com/hq/s/%s' % symbol
        content = HttpHelper.http_get(url)
        value = string_fetch(content, 'class=\"price\">', '</td>')
        return float(value)


if __name__ == '__main__':
    # print MarketWatchScraper().get_current_data('SVXY')
    # print YahooScraper().get_current_data('SVXY')
    # print CNBCScraper().get_current_data('SVXY')
    print LaoHu8Scraper().get_current_data('SVXY')