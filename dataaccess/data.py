import pandas as pd
from utils.logger import Logger
from common.pathmgr import PathMgr
from common.symbols import Symbols
from common.tradetime import TradeTime
from dataaccess.yahooequitydao import YahooEquityDAO


class DBProvider(object):

    def __init__(self, logger=Logger(__name__, None)):
        self.logger = logger

    def history(self, symbol, field, window):
        fields_dic = {'open': 'openPrice', 'close': 'adjclosePrice', 'high': 'highPrice', 'low': 'lowPrice',
                      'price': 'adjclosePrice'}
        fields = fields_dic.keys()
        if field.lower() not in field:
            raise Exception('the field should be in %s...'%fields)
        price_field = fields_dic[field]
        yahoo_symbol = Symbols.get_mapped_symbol(symbol)
        from_date = TradeTime.get_from_date_by_window(window)
        rows = YahooEquityDAO().get_all_equity_price_by_symbol(yahoo_symbol, from_date.strftime('%Y-%m-%d'), price_field)
        return rows


class Data(object):

    def __init__(self):
        self.logger = Logger(__name__, PathMgr.get_log_path())
        self.historical_data_provider = DBProvider()

    def history(self, assets, field='price', window=30, frequency='1d'):
        """
        get the history data
        :param assets: symbol likes SPX, SPY, VIX, QQQ, etc, or iterable asset
        :param field: support open, close, high, low, price, the price = close
        :param window: the count of records.
        :param frequency: this parameter used for compatible with quantopian algorithm.
        :return:
        """
        frequency = '1d'
        if hasattr(assets, '__iter__'):
            results = None
            columns = ['date']
            for symbol in assets:
                print symbol
                columns.append(symbol)
                rows = self.historical_data_provider.history(symbol, field, window)
                if results is None:
                    results = map(list, rows)
                else:
                    map(lambda x, y: x.append(y[1]), results, rows)
            df = pd.DataFrame(map(lambda x: x[1:], results), index=map(lambda x: x[0], results), columns=columns[1:])
            return df
        else:
            symbol = str(assets)
            rows = self.historical_data_provider.history(symbol, field, window)
            df = pd.DataFrame(map(lambda x: x[1:], rows), index=map(lambda x: x[0], rows), columns = ['price'])
            return df

if __name__ == '__main__':
    data = Data()
    #print data.history('QQQ', field='close', window=100)
    #print data.history('SPX')
    #print data.history(['SPY', 'VIX'], window=252)
    print data.history(['xiv', 'vxx'], window=17)