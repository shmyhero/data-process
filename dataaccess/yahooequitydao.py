import pandas as pd
from dataaccess.basedao import BaseDAO
from common.etfs import ETFS
from common.pathmgr import PathMgr


class YahooEquityDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

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
        for symbol in ETFS.get_all_symbols():
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

    def save_all(self):
        for symbol in ETFS.get_all_symbols():
            self.logger.info('save data for %s...' %symbol)
            path = PathMgr.get_historical_etf_path(symbol)
            df = pd.read_csv(path)
            self.save(symbol, df)


if __name__ == '__main__':
    YahooEquityDAO().save_all()
