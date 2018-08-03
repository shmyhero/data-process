from utils.httphelper import HttpHelper
from utils.stringhelper import string_fetch


class CNBCScraper():

    @staticmethod
    def get_data_by_symbol(symbol):
        url = 'https://www.cnbc.com/quotes/?symbol=%s' % symbol
        content = HttpHelper.http_get(url)
        value = string_fetch(content, '\"previous_day_closing\":\"', '\"')
        return float(value.replace(',', ''))


if __name__ == '__main__':
    print CNBCScraper.get_data_by_symbol('VIX')