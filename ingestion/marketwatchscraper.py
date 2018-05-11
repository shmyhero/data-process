from utils.httphelper import HttpHelper
from utils.stringhelper import string_fetch


class MarketWatchScraper():

    @staticmethod
    def get_data_by_symbol(symbol):
        url = 'https://www.marketwatch.com/investing/fund/%s' % symbol
        content = HttpHelper.http_get(url)
        content = string_fetch(content, 'mw-rangeBar precision=', 'Day Low')
        value = string_fetch(content, '\"last-value\">', '</span>')
        return float(value.replace(',', ''))
