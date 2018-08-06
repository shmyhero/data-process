import datetime
from utils.stringhelper import string_fetch
from utils.httphelper import HttpHelper
from utils.iohelper import write_to_file
from common.pathmgr import PathMgr
from common.tradetime import TradeTime
from common.symbols import Symbols
from dataaccess.optiondao import OptionDAO
from entities.option import Option


class BigChartsScraper(object):

    def __init__(self):
        pass

    @staticmethod
    def get_option_content(symbol, url_template):
        #url = 'http://bigcharts.marketwatch.com/quickchart/options.asp?symb={}&showAll=True'.format(symbol)
        url = url_template.format(symbol)
        content = HttpHelper.http_get(url)
        if 'showAll' in url:
            file_path = PathMgr.get_bigcharts_option_symbol_path(symbol + '2')
        else:
            file_path = PathMgr.get_bigcharts_option_symbol_path(symbol + '1')
        write_to_file(file_path, content)
        return content

    @staticmethod
    def find_type_and_month(c):
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWX'
        founded_index = None
        for index, letter in enumerate(letters):
            if letter == c:
                founded_index = index
                break
        if founded_index < 12:
            option_type = 'Call'
        else:
            option_type = 'Put'
        month = founded_index % 12 + 1
        return option_type, month

    @staticmethod
    def parse_for_option(bigcharts_option_symbol, underlying_symbol, last_price):
        if last_price == '':
            return None
        content = bigcharts_option_symbol[len(underlying_symbol):]
        option_type, month = BigChartsScraper.find_type_and_month(content[0])
        date = int(content[1:3])
        year = int(content[3:5])
        expiration_date = datetime.date(year + 2000, month, date)
        strike_price = int(content[6:])/pow(10, int(content[5]))
        option_symbol = '%s%s%s%08d' % (underlying_symbol, expiration_date.strftime('%y%m%d'), option_type[0], strike_price * 1000)
        option = Option()
        option.optionType = option_type
        option.tradeTime = TradeTime.get_latest_trade_date()
        option.symbol = option_symbol
        option.expirationDate = expiration_date
        if '^'+underlying_symbol in Symbols.indexes:
            option.underlingSymbol = '^'+underlying_symbol
        else:
            option.underlingSymbol = underlying_symbol
        option.strikePrice = strike_price
        option.daysToExpiration = (expiration_date - option.tradeTime).days
        option.lastPrice = float(last_price)
        return option

    @staticmethod
    def parse_options(underlying_symbol, content):
        items = content.split('optionticker')[1:]
        options = []
        for item in items:
            bigcharts_option_symbol = string_fetch(item, 'title=\"', '\"')
            last_price = string_fetch(string_fetch(item, 'quote</a></td>', ''), '>', '</td>')
            option = BigChartsScraper.parse_for_option(bigcharts_option_symbol, underlying_symbol, last_price)
            if option is not None:
                options.append(option)
        return options

    @staticmethod
    def ingest_options(symbol):
        url_templates = ['http://bigcharts.marketwatch.com/quickchart/options.asp?symb={}',
                         'http://bigcharts.marketwatch.com/quickchart/options.asp?symb={}&showAll=True']
        for url_template in url_templates:
            content = BigChartsScraper.get_option_content(symbol, url_template)
            options = BigChartsScraper.parse_options(symbol, content)
            OptionDAO().insert(options)


if __name__ == '__main__':
    print BigChartsScraper.ingest_options('VIX')
    # print BigChartsScraper.ingest_options('VXX')
    print BigChartsScraper.ingest_options('SPY')
    # from utils.iohelper import read_file_to_string, get_sub_files
    # for file in get_sub_files(PathMgr.get_bigcharts_option_dir(sub_path='2018-04-20')):
    #     content = read_file_to_string(file)
    #     options = BigChartsScraper.parse_options('VIX', content)
    #     OptionDAO().insert(options)