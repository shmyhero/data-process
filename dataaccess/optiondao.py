import sys
import datetime
import pandas as pd
from common.tradetime import TradeTime
from dataaccess.basedao import BaseDAO


class OptionDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into option_data (underlingSymbol, tradeTime, symbol, expirationDate,the_date,daysToExpiration,optionType,strikePrice,askPrice,bidDate,bidPrice,openPrice,highPrice,lowPrice,lastPrice,priceChange,volatility,theoretical,delta,gamma,rho,theta,vega,openInterest,volume) values ('{}','{}','{}','{}','{}',{},'{}',{},{},'{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        count = 0
        for option in records:
            query = BaseDAO.mysql_format(query_template, option.underlingSymbol, option.tradeTime, option.symbol,option.expirationDate,option.date,option.daysToExpiration,option.optionType,option.strikePrice,option.askPrice,option.bidDate,option.bidPrice,option.openPrice,option.highPrice,option.lowPrice,option.lastPrice,option.priceChange,option.volatility,option.theoretical,option.delta,option.gamma,option.rho,option.theta,option.vega,option.openInterest,option.volume)
            self.execute_query(query, cursor)
            count += 1
            if count == 1000:
                conn.commit()
                count = 0
        conn.commit()
        conn.close()

    def get_option_price_by_date(self, option_symbol, date_str, price_field='lastPrice', cursor=None):
        """
        :param self:
        :param option_symbol:
        :param date_str:
        :param price_field: lastprice(close price) in default
        :param cursor:
        :return:
        """
        query_template = """select {} from option_data where symbol = '{}' and tradeDate <= str_to_date('{}', '%Y-%m-%d') order by tradeDate desc limit 1"""
        query = query_template.format(price_field, option_symbol, date_str)
        rows = self.select(query, cursor)
        if rows is None or len(rows) < 1:
            return None
        else:
            return rows[0][0]

    def get_all_unexpired_dates(self, equity_symbol, from_date=None, cursor = None):
        from_date = from_date or TradeTime.get_latest_trade_date()
        query_template = """select distinct(expirationDate) from  option_data 
                                    where underlingSymbol = '{}' and expirationDate > str_to_date('{}', '%Y-%m-%d')
                                    order by expirationDate"""
        query = query_template.format(equity_symbol, from_date.strftime('%Y-%m-%d'))
        rows = self.select(query, cursor)
        return map(lambda x: x[0], rows)

    def get_following_expirationDate(self, equity_symbol, from_date=None):
        from_date = from_date or TradeTime.get_latest_trade_date()
        dates = self.get_all_unexpired_dates(equity_symbol, from_date)
        for d in dates:
            if d.weekday() == 4 and 14 < d.day < 22:
                return d

    def get_strike_prices_by(self, equity_symbol, str_expirationDate):
        query_template = """select distinct strikePrice from option_data where underlingsymbol = '{}'  and expirationDate = str_to_date('{}', '%Y-%m-%d') order by strikePrice"""
        query = query_template.format(equity_symbol, str_expirationDate)
        rows = self.select(query)
        return map(lambda x: x[0], rows)

    def get_option_by(self, equity_symbol, str_expirationDate, strike_price, option_type):
        query_template = """select symbol, tradetime, lastPrice, delta, gamma, vega, theta, rho from option_data where underlingsymbol = '{}' and expirationDate = str_to_date('{}', '%Y-%m-%d') and strikePrice = {} and optionType = '{}' order by tradeTime"""
        query = query_template.format(equity_symbol, str_expirationDate, strike_price, option_type)
        rows = self.select(query)
        return rows

    def get_option_by_symbol(self, option_symbol):
        query_template = """select tradetime, lastPrice, delta, gamma, vega, theta, rho from option_data where symbol = '{}' order by tradeTime"""
        query = query_template.format(option_symbol)
        rows = self.select(query)
        return rows

    def get_delta_by_symbol_and_date(self, option_symbol, trade_time, cursor=None):
        query_template = """select delta from option_data where symbol = '{}' and tradeTime = str_to_date('{}', '%Y-%m-%d') limit 1"""
        query = query_template.format(option_symbol, trade_time)
        rows = self.select(query, cursor)
        #print query
        #print rows
        if len(rows) == 0:
            return None
        else:
            return rows[0][0]

    def find_symbol(self, equity_symbol, expiration_date, current_equity_price, imp_only = False, current_date=None, days_to_current_date = 30, option_type='Call', cursor = None):
        """
        find the at the money option symbol
        :param equity_symbol:
        :param expiration_date:
        :param current_equity_price:
        :param imp_only: in the money option only.
        :param current_date:
        :param days_to_current_date:
        :param cursor:
        :return: option symbol like SPY170915C00245000
        """
        current_date = current_date or  datetime.date.today()
        query_template = """select distinct(strikeprice) as strikeprice, min(tradeTime) from  option_data where underlingSymbol = '{}'  and  expirationDate = str_to_date('{}', '%Y-%m-%d') and optionType = '{}' group by strikeprice order by min(tradeTime)"""
        query = query_template.format(equity_symbol, expiration_date.strftime('%Y-%m-%d'), option_type)
        rows = self.select(query, cursor)
        start_date = max(current_date - datetime.timedelta(days=days_to_current_date), rows[0][1])
        filtered_rows = filter(lambda x: x[1] <= start_date, rows)
        #print filtered_rows
        min = sys.maxint
        strike_price = None
        for row in filtered_rows:
            if imp_only:
                delta = row[0] - current_equity_price
                if 0 < delta < min:
                    min = delta
                    strike_price = row[0]
            else:
                delta = abs(row[0] - current_equity_price)
                if delta < min:
                    min = delta
                    strike_price = row[0]

        # eg. 'SPY170915C00245000'
        if strike_price is None:
            return None
        else:
            return '%s%s%s%08d' % (equity_symbol, expiration_date.strftime('%y%m%d'), option_type[0], strike_price * 1000)

    def get_implied_volatilities(self, option_symbol):
        query_template = """select tradeTime, volatility from option_data where symbol = '{}'"""
        query = query_template.format(option_symbol)
        rows = self.select(query)
        return rows

    def get_delta(self, option_symbol):
        query_template = """select tradeTime, delta from option_data where symbol = '{}'"""
        query = query_template.format(option_symbol)
        rows = self.select(query)
        return rows

    def get_corresponding_implied_volatilities(self, equity_symbol, current_equity_price):
        exp_date = self.get_following_expirationDate(equity_symbol) #get recent exp_date for this symbol
        option_symbol = self.find_symbol(equity_symbol, exp_date, current_equity_price)
        rows = self.get_implied_volatilities(option_symbol)
        return rows

    def get_corresponding_delta(self, equity_symbol, current_equity_price, days_to_current_date=10):
        exp_date = self.get_following_expirationDate(equity_symbol)  # get recent exp_date for this symbol
        option_symbol = self.find_symbol(equity_symbol, exp_date, current_equity_price, days_to_current_date=days_to_current_date)
        rows = self.get_delta(option_symbol)
        return rows

    def get_vix_options(self):
        query = """select symbol, tradeTime, daysToExpiration, strikePrice, optiontype from option_data where underlingSymbol = '^VIX'"""
        return self.select(query)

    def update_delta_for_vix_options(self, symbol, tradeTime, delta, cursor):
        query_template = """update option_data set delta = {} where underlingSymbol = '^VIX' and symbol = '{}' and tradeTime = '{}'"""
        query = query_template.format(delta, symbol, tradeTime)
        self.execute_query(query, cursor)


if __name__ == '__main__':
    #exp_date = OptionDAO().get_following_expirationDate('SPY')
    #print exp_date
    #print OptionDAO().find_symbol('SPY', exp_date, 245.38)
    #print OptionDAO().get_corresponding_implied_volatilities('SPY', 245.38)
    #print OptionDAO().get_spike_prices_by('SPY', '2017-09-15')
    #print OptionDAO().get_option_by('SPY', '2017-09-15', 245, 'Call')
    print OptionDAO().get_option_by_symbol('SPY170915C00245000')





