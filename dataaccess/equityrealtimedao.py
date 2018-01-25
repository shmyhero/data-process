import datetime
import pytz
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
            if i == 390:
                print time
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
    def add_missing_data_in_real_time(self, symbol='XIV', ):
        us_dt = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
        now = datetime.datetime(us_dt.year, us_dt.month, us_dt.day, us_dt.hour, us_dt.minute, us_dt.second)
        if TradeTime.is_trade_day(now.date()):
            default_start_time = datetime.datetime(now.year, now.month, now.day, 9, 30, 0)
            start_time = max(default_start_time, datetime.datetime(now.year, now.month, now.day, now.hour-1, now.minute, 0))
            if now > start_time:
                if TradeTime.is_half_trade_day(now.date()):
                    default_end_time = datetime.datetime(now.year, now.month, now.day, 13, 0, 0)
                else:
                    default_end_time = datetime.datetime(now.year, now.month, now.day, 16, 0, 0)
                end_time = min(now, default_end_time)
                if end_time > start_time:
                    minutes_count = range((end_time - start_time).seconds/60 + 1)
                    trade_minutes = map(lambda x: start_time + datetime.timedelta(minutes=x), minutes_count)
                    # print trade_minutes
                    rows = self.get_min_time_and_price(symbol, start_time, end_time)
                    # print rows
                    j = 0
                    missing_records = []
                    # self.logger.info('rows = %s, \n trade_minutes = %s' %(rows[-2:], trade_minutes[-2:]))
                    for i, time in enumerate(trade_minutes):
                        if j >= len(rows):
                            break # rows length may less than trade_minutes for 1 elements.
                        if rows[j][0].minute > time.minute:
                            if j > 0:
                                price = rows[j - 1][1]
                            else:
                                price = rows[0][1]
                            # self.logger.info('missing record: j = %s, time=%s'%(j, time))
                            missing_records.append((symbol, time, price))
                        else:
                            j = j + 1
                    if len(missing_records) > 0:
                        for record in missing_records:
                            self.insert(*record)
                    return len(missing_records)

if __name__ == '__main__':
    # rows = EquityRealTimeDAO().get_min_time_and_price(start_time=datetime.datetime(2018, 1, 22, 0, 0, 0))
    # for row in rows:
    #     print row
    # EquityRealTimeDAO().add_missing_data()
    # EquityRealTimeDAO().add_missing_data(validate_date=datetime.date(2018, 1, 19))
    EquityRealTimeDAO().add_missing_data_in_real_time()