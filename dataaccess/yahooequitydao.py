import pandas as pd
from dataaccess.basedao import BaseDAO
from common.symbols import Symbols
from common.pathmgr import PathMgr


class YahooEquityDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def get_equity_price_by_date(self, symbol, date_str, price_field = 'closePrice', cursor=None):
        """
        :param symbol:
        :param date_str: the format is 'YYYY-mm-dd'
        :param price_field:
        :return: price
        """
        query_template = """select {} from yahoo_equity where symbol = '{}' and tradeDate <= str_to_date('{}', '%Y-%m-%d') order by tradeDate desc limit 1"""
        query = query_template.format(price_field, symbol, date_str)
        rows = self.select(query, cursor)
        if rows is None or len(rows) < 1:
            return None
        else:
            return rows[0][0]

    def get_all_equity_price_by_symbol(self, symbol, from_date_str='1993-01-01', price_field = 'adjClosePrice'):
        query_template = """select tradeDate, {} from yahoo_equity where symbol = '{}' and tradeDate >= str_to_date('{}', '%Y-%m-%d') order by tradeDate"""
        query = query_template.format(price_field, symbol, from_date_str)
        rows = self.select(query)
        return rows

    def get_equity_monthly_by_symbol(self, symbol, columns):
        """
        :param symbol: eg: SPY
        :return: rows
        """
        columns_sql = ', '.join(columns)
        query_template = """select {} from yahoo_equity_monthly_view where symbol = '{}'"""
        query = query_template.format(columns_sql, symbol)
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df

    def get_latest_price(self, symbol):
        query_template = """select closePrice from yahoo_equity where symbol = '{}' order by tradeDate desc limit 1"""
        query = query_template.format(symbol)
        rows = self.select(query)
        return rows[0][0]

    def insert(self, symbol, df):
        query_template = """insert into yahoo_equity (symbol,tradeDate,openPrice,highPrice,lowPrice,closePrice,adjClosePrice,volume) values ('{}','{}',{},{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            query = BaseDAO.mysql_format(query_template, symbol, row['Date'], row['Open'], row['High'],
                                         row['Low'], row['Close'], row['Adj Close'], row['Volume'])
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def insert_all(self):
        for symbol in Symbols.get_all_symbols():
            self.logger.info('insert data for %s...' %symbol)
            path = PathMgr.get_historical_etf_path(symbol)
            df = pd.read_csv(path)
            self.insert(symbol, df)

    def save(self, symbol, df):
        query_template = """insert into yahoo_equity (symbol,tradeDate,openPrice,highPrice,lowPrice,closePrice,adjClosePrice,volume) values 
                           ('{}','{}',{},{},{},{},{},{}) on duplicate key update adjClosePrice = {}"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            query = BaseDAO.mysql_format(query_template, symbol, row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume'], row['Adj Close'])
            #print query
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def save_all(self, symbols = Symbols.get_all_symbols()):
        for symbol in symbols:
            self.logger.info('save data for %s...' %symbol)
            path = PathMgr.get_historical_etf_path(symbol)
            df = pd.read_csv(path)
            self.save(symbol, df)


if __name__ == '__main__':
    #YahooEquityDAO().save_all(['^GSPC'])
    YahooEquityDAO().save_all(['^GSPC', '^DJI'])
    #print YahooEquityDAO().get_latest_price('SPY')
    #print YahooEquityDAO().get_equity_price_by_date('SPY', '2017-08-05')
    #print YahooEquityDAO().get_equity_monthly_by_symbol('SPY', ['symbol', 'lastdate', 'closeprice', 'adjcloseprice', 'tradeyear', 'trademonth'])
    #print YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str='2017-08-01')
