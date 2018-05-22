import datetime
from dataaccess.basedao import BaseDAO


class Equity30MinDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into equity_30min (symbol,tradeTime,openPrice,highPrice,lowPrice,closePrice,volume)
                            values ('{}','{}',{},{},{},{},{})
                            on duplicate key update openPrice={},highPrice={},lowPrice={},closePrice={},volume={}
                         """
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        for equity in records:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.volume, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def get_time_and_price(self, symbol='SPY', start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        query = """select tradeTime, closePrice from equity_30min where tradeTime >= '{}' and tradeTime <= '{}' and symbol = '{}' and tradeTime not like '%09:30:00' order by tradeTime""".format(start_time, end_time, symbol)
        return self.select(query)


if __name__ == '__main__':
    records = Equity30MinDAO().get_time_and_price(start_time=datetime.datetime(2018, 1, 1, 0, 0, 0))
    print records