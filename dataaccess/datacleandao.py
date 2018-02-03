import datetime
from entities.vix import VIX
from dataaccess.basedao import BaseDAO
from dataaccess.vixdao import VIXDAO
from dataaccess.equitymindao import EquityMinDAO
from dataaccess.equityrealtimedao import EquityRealTimeDAO


class DataCleanDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    # found the records with trade time on Saturday, remove it.
    def clean_equity_data(self):
        query = """delete from equity where tradeTime = str_to_date('2017-09-23', '%Y-%m-%d')"""
        self.execute_query(query)

    # found the trade time error in database, fix it...
    def fix_option_date_error1(self):
        query = """update option_data set tradetime = str_to_date('2017-08-04', '%Y-%m-%d') where tradeTime <> the_date and tradeTime = str_to_date('2017-08-05', '%Y-%m-%d')"""
        self.execute_query(query)

    def fix_option_date_error2(self):
        query = """delete from option_data where tradeTime = str_to_date('2017-09-23', '%Y-%m-%d')"""
        self.execute_query(query)

    def add_missing_data_for_vix(self):
        viq17 = VIX(symbol='VIQ17', lastPrice=12.160, dailyHighPrice=12.560, dailyLowPrice=11.900, dailyLastPrice=12.160,\
                  previousPrice=12.325, dailyPreviousPrice=12.325, volume=10365,dailyDate1dAgo= '2017-08-16')
        VIXDAO().insert([viq17])

    def delete_option(self, underlying_symbol):
        query_template = """delete from option_data where underlingSymbol = '{}'"""
        query = query_template.format(underlying_symbol)
        self.execute_query(query)

    def remove_invalid_records(self, date):
        query_template = """delete from option_data where tradetime = '{}'"""
        query = query_template.format(str(date))
        self.execute_query(query)

    def add_missing_data_to_realtime_from_min(self, date):
        start_time = datetime.datetime.fromordinal(date.toordinal())
        end_time = start_time + datetime.timedelta(days=1)
        rows = EquityMinDAO().get_time_and_price(start_time=start_time, end_time=end_time)
        for row in rows:
            EquityRealTimeDAO().insert('XIV', row[0], row[1])


if __name__ == '__main__':
    #DataCleanDAO().add_missing_data_for_vix()
    #DataCleanDAO().fix_option_date_error1()
    #DataCleanDAO().delete_option('VIX')
    #DataCleanDAO().remove_invalid_records(datetime.date(2017, 9, 23))
    #DataCleanDAO().fix_option_date_error2()
    # DataCleanDAO().clean_equity_data()
    DataCleanDAO().add_missing_data_to_realtime_from_min(datetime.date(2018, 2, 2))

