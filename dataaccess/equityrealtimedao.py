import datetime
from common.tradetime import TradeTime
from dataaccess.basedao import BaseDAO


class EquityRealTimeDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, symbol, trade_time, price):
        query_template = """insert into equity_realtime (symbol,tradeTime,price) values ('{}','{}',{})"""
        query = BaseDAO.mysql_format(query_template, symbol, trade_time, price)
        self.execute_query(query)

    def get_time_and_price(self, symbol='XIV', start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        query = """select tradeTime, price from equity_realtime where tradeTime >= '{}' and tradeTime <= '{}' and symbol = '{}' order by tradeTime """.format(start_time, end_time, symbol)
        return self.select(query)

    def get_min_time_and_price(self, symbol='XIV', start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        rows = self.get_time_and_price(symbol, start_time, end_time)
        new_rows = []
        last_min = -1
        for row in rows:
            trade_time = row[0]
            if last_min != trade_time.minute:
                last_min = trade_time.minute
                new_rows.append(row)
        return new_rows

    def add_missing_data(self, symbol='XIV', validate_date=None):
        if validate_date is None:
            validate_date = TradeTime.get_latest_trade_date()
        start_time = datetime.datetime.fromordinal(validate_date.toordinal())
        end_time = start_time + datetime.timedelta(days=1)
        rows = self.get_min_time_and_price(symbol, start_time, end_time)
        j = 0
        missing_records = []
        for i, time in enumerate(TradeTime.get_all_trade_min(validate_date)):
            if j >= len(rows) or rows[j][0].minute > time.minute:
                if j > 0:
                    price = rows[j-1][1]
                else:
                    price = rows[0][1]
                missing_records.append((symbol, time, price))
            else:
                j = j+1
        if len(missing_records) > 0:
            for record in missing_records:
                self.insert(*record)
        return len(missing_records)

    # TODO: complete this...
    def add_missing_data_in_real_time(self):
        pass

if __name__ == '__main__':
    # rows = EquityRealTimeDAO().get_min_time_and_price(start_time=datetime.datetime(2018, 1, 22, 0, 0, 0))
    # for row in rows:
    #     print row
    # EquityRealTimeDAO().add_missing_data()
    EquityRealTimeDAO().add_missing_data(validate_date=datetime.date(2018, 1, 19))