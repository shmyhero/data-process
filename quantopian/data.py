import pandas as pd
import datetime
from common.tradetime import TradeTime
from dataaccess.yahooequitydao import YahooEquityDAO


class MyData(object):

    fields_dic = {'open':'openPrice', 'close':'adjclosePrice', 'high':'highPrice', 'low':'lowPrice', 'price':'adjclosePrice'}

    @staticmethod
    def history(symbol, field = 'price', window = 30 ):
        fields = MyData.fields_dic.keys()
        if field.lower() not in field:
            raise Exception('the field should be in %s...'%fields)
        price_field = MyData.fields_dic[field]
        from_date = TradeTime.get_latest_trade_date() - datetime.timedelta(window * 2)
        rows = YahooEquityDAO().get_all_equity_price_by_symbol(symbol, from_date.strftime('%Y-%m-%d'), price_field)
        df = pd.DataFrame(rows[-window:])
        df.columns = ['date', 'price']
        return df


if __name__ == '__main__':
    print MyData.history('QQQ', field = 'close', window = 100)