import json
from utils.logger import Logger
from common.pathmgr import PathMgr
from utils.httphelper import HttpHelper
from entities.equity import Equity


class AlphaVantage(object):

    def __init__(self, apikey='JW72YXW7G33OWE5S'):
        self.logger = Logger(__name__, PathMgr.get_log_path('minutes'))
        self.apikey = apikey

    def parse_record(self, content, symbol):
        json_data = json.loads(content)
        dic_data = json_data['Time Series (1min)']
        for key, value in dic_data.iteritems():
            time = key
            open = value['1. open']
            high = value['2. high']
            low = value['3. low']
            close = value['4. close']
            # volume = value['5. volume']
            equity = Equity(symbol, time, open, high, low, close, None, None)
            yield equity

    def get_minutes_equites(self, symbol):
        url_template = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=1min&apikey=%s'
        url = url_template % (symbol, self.apikey)
        content = HttpHelper.http_get(url)
        return list(self.parse_record(content, symbol))


if __name__ == '__main__':
    for equity in AlphaVantage().get_minutes_equites('SVXY'):
        print equity
