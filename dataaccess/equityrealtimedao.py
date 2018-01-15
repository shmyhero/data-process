import datetime
import pandas as pd
from dataaccess.basedao import BaseDAO


class EquityRealTimeDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into equity_realtime (symbol,tradeTime,openPrice,highPrice,lowPrice,closePrice,volume) values ('{}','{}',{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        for equity in records:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()
