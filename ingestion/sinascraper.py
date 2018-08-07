from utils.httphelper import HttpHelper
from utils.stringhelper import string_fetch


class SINAScraper():

    @staticmethod
    def get_data_by_symbol(symbol):
        url = 'http://hq.sinajs.cn/?list=gb_%s' % symbol.replace('.', '$').lower()
        content = HttpHelper.http_get(url)
        value = string_fetch(content, ',', ',')
        return float(value)


if __name__ == '__main__':
    # print SINAScraper.get_data_by_symbol('BRK.A')
    print SINAScraper.get_data_by_symbol('VIX')