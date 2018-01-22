import datetime
import pandas as pd
from dataaccess.basedao import BaseDAO


class EquityMinDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into equity_min (symbol,tradeTime,openPrice,highPrice,lowPrice,closePrice,volume) values ('{}','{}',{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        for equity in records:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def get_time_and_price(self, start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        query = """select tradeTime, closePrice from equity_min where tradeTime > '{}' and tradeTime < '{}' and symbol = 'XIV' order by tradeTime""".format(start_time, end_time)
        return self.select(query)

if __name__ == '__main__':
    rows = EquityMinDAO().get_time_and_price(datetime.datetime(2018, 1, 19, 9, 30, 0))
    for row in rows:
        print row
