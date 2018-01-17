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
