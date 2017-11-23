import datetime
import pandas as pd
from dataaccess.basedao import BaseDAO


class EquityDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into equity (symbol,tradeTime,openPrice,highPrice,lowPrice,lastPrice,priceChange,volume) values ('{}','{}',{},{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        for equity in records:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.priceChange, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def select_by_symbols(self, symbols):
        columns = ['symbol', 'tradeTime', 'openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'priceChange', 'volume']
        fields = ', '.join(columns)
        symbols_sql = ', '.join(map(lambda x: '\'%s\''%x, symbols))
        query_template = """select {} from equity where symbol in ({})"""
        query = query_template.format(fields, symbols_sql)
        #print query
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df

    def get_date_price_list(self, symbol, days_to_now = 30):
        start_date = datetime.datetime.now() - datetime.timedelta(days_to_now)
        # query_template = """select tradeTime, lastPrice from equity where symbol = '{}' and tradeTime >= str_to_date('{}', '%Y-%m-%d')"""
        # query = query_template.format(symbol, start_date.strftime('%Y-%m-%d'))
        # rows = self.select(query)
        rows = self.get_all_equity_price_by_symbol(symbol, start_date)
        df = pd.DataFrame(rows)
        df.columns = ['date', 'price']
        return df

    def get_all_equity_price_by_symbol(self, symbol, from_date=datetime.date(2017, 7, 24)):
        from_date_str = from_date.strftime('%Y-%m-%d')
        query_template = """select tradeTime, lastPrice from equity where symbol = '{}' and tradeTime >= str_to_date('{}', '%Y-%m-%d') order by tradeTime"""
        query = query_template.format(symbol, from_date_str)
        rows = self.select(query)
        return rows

    def get_equity_price_by_date(self, symbol, date, price_field = 'lastPrice', cursor=None):
        """
        :param symbol: equity symbol
        :param date: the date of equity price
        :param price_field: default as last price
        :param cursor:
        :return: equity price
        """
        query_template = """select {} from equity where symbol = '{}' and tradetime <= str_to_date('{}', '%Y-%m-%d') order by tradeTime desc limit 1"""
        query = query_template.format(price_field, symbol, date.strftime('%Y-%m-%d'))
        rows = self.select(query, cursor)
        if rows is None or len(rows) < 1:
            return None
        else:
            return rows[0][0]

    def get_price_change_percentage(self, from_date, to_date):
        query_template = """select t1.symbol, (t2.end_price - t1.start_price)/t1.start_price as percentage from 
                        (select symbol, lastPrice as start_price from equity where tradeTime = str_to_date('2017-07-24', '%Y-%m-%d')) as t1,
                        (select symbol, lastPrice as end_price from equity where tradeTime = str_to_date('2017-07-26', '%Y-%m-%d')) as t2
                        where t1.symbol = t2.symbol order by percentage desc"""
        query = query_template.format(from_date, to_date)
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = ['symbol', 'price_change_percentage']
        return df

    def get_latest_price(self, symbol):
        query_template = """select lastPrice from equity where symbol = '{}' order by tradetime desc limit 1"""
        query = query_template.format(symbol)
        rows = self.select(query)
        return rows[0][0]


if __name__ == '__main__':
    #df = EquityDAO().get_price_change_percentage('2017-07-24', '2017-07-26')
    #print df
    #df_left =
    #print df[df.symbol.any(['IXC', 'IXP', 'UNG', 'IDU', 'GLD'])]
    #print EquityDAO().get_date_price_list('SPY')
    print EquityDAO().get_latest_price('SPY')
