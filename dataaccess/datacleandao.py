import datetime
from common.tradetime import TradeTime
from entities.vix import VIX
from dataaccess.basedao import BaseDAO
from dataaccess.vixdao import VIXDAO
from dataaccess.equitymindao import EquityMinDAO
from dataaccess.equityrealtimedao import EquityRealTimeDAO
from dataaccess.optiondao import OptionDAO


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

    def add_missing_data_to_realtime_from_min(self, date, symbol='SVXY'):
        start_time = datetime.datetime.fromordinal(date.toordinal())
        end_time = start_time + datetime.timedelta(days=1)
        rows = EquityMinDAO().get_time_and_price(symbol=symbol, start_time=start_time, end_time=end_time)
        rows = map(list, rows)
        rows[0][0] = rows[0][0] + datetime.timedelta(seconds=1)
        for row in rows:
            EquityRealTimeDAO().insert(symbol, row[0], row[1])

    def remove_market_open_data_for_min(self):
        EquityMinDAO().remove_market_open_records()

    def add_missing_date_for_option(self, from_date, to_date):
        query_template = """select underlingSymbol, tradeTime, symbol, expirationDate, the_date,  daysToExpiration, optionType, strikePrice, lastPrice, volatility, delta, gamma, rho, theta, vega 
                            from option_data 
                            where underlingSymbol = 'VXX' and tradeTime = '{}'
                          """
        query = query_template.format(from_date)
        rows = self.select(query)
        insert_template = """insert into option_data (underlingSymbol, tradeTime, symbol, expirationDate,the_date, daysToExpiration, optionType,strikePrice,lastPrice,volatility,delta,gamma,rho,theta,vega)
        values ('{}','{}','{}','{}','{}',{},'{}',{},{},{},{},{},{},{},{})         
        """
        for row in rows:
            (underlingSymbol, tradeTime, symbol, expirationDate, the_date, daysToExpiration, optionType, strikePrice,
             lastPrice, volatility, delta, gamma, rho, theta, vega) = row
            tradeTime = to_date
            daysToExpiration += (from_date - to_date).days
            insert_query = insert_template.format(underlingSymbol, tradeTime, symbol, expirationDate, the_date, daysToExpiration, optionType, strikePrice,
             lastPrice, volatility, delta, gamma, rho, theta, vega)
            insert_query = insert_query.replace('None', 'null')
            print insert_query
            self.execute_query(insert_query)

    def clear_invalid_date_records(self):
        query = """select distinct TradeDate from yahoo_equity"""
        remove_invalid_query_template = """delete from yahoo_equity where TradeDate = '{}'"""
        rows = self.select(query)
        dates = map(lambda x: x[0], rows)
        for date in dates:
            if not TradeTime.is_trade_day(date):
                query = remove_invalid_query_template.format(date)
                print date
                print query
                self.execute_query(query)





if __name__ == '__main__':
    #DataCleanDAO().add_missing_data_for_vix()
    #DataCleanDAO().fix_option_date_error1()
    #DataCleanDAO().delete_option('VIX')
    #DataCleanDAO().remove_invalid_records(datetime.date(2017, 9, 23))
    #DataCleanDAO().fix_option_date_error2()
    # DataCleanDAO().clean_equity_data()
    # DataCleanDAO().add_missing_data_to_realtime_from_min(datetime.date(2018, 8, 3), 'SPY')
    # DataCleanDAO().add_missing_date_for_option(datetime.date(2018, 5, 18), datetime.date(2018, 5, 17))
    DataCleanDAO().clear_invalid_date_records()