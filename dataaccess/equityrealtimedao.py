import datetime
import pandas as pd
from dataaccess.basedao import BaseDAO


class EquityRealTimeDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, symbol, trade_time, price):
        query_template = """insert into equity_realtime (symbol,tradeTime,price) values ('{}','{}',{})"""
        query = BaseDAO.mysql_format(query_template, symbol, trade_time, price)
        self.execute_query(query)

    def get_time_and_price(self, start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        query = """select tradeTime, price from equity_realtime where tradeTime > '{}' and tradeTime < '{}' order by tradeTime """.format(start_time, end_time)
        return self.select(query)

    def get_min_time_and_price(self, start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        rows = self.get_time_and_price(start_time, end_time)
        new_rows = []
        last_min = -1
        for row in rows:
            trade_time = row[0]
            if last_min != trade_time.minute:
                last_min = trade_time.minute
                new_rows.append(row)
        return new_rows

if __name__ == '__main__':
    rows = EquityRealTimeDAO().get_min_time_and_price(datetime.datetime(2018, 1, 17, 0, 0, 0))
    for row in rows:
        print row