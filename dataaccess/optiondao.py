import sys
import datetime
import pandas as pd
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

    def get_following_expirationDate(self, equity_symbol, from_date_str=datetime.datetime.today().strftime('%Y-%m-%d')):
        query_template = """select distinct(expirationDate) from  option_data 
                            where underlingSymbol = '{}' and expirationDate >= str_to_date('{}', '%Y-%m-%d')
                            order by expirationDate"""
        query = query_template.format(equity_symbol, from_date_str)
        rows = self.select(query)
        for row in rows:
            d = row[0]
            if d.weekday() == 4 and 14 < d.day < 22:
                return d

    def find_symbol(self, equity_symbol, expration_date, current_equity_price, days_to_now = 30):
        query_template = """select distinct(strikeprice) as strikeprice, min(tradeTime) from  option_data where underlingSymbol = '{}'  and  expirationDate =  str_to_date('{}', '%Y-%m-%d') and optionType = 'Call' group by strikeprice order by min(tradeTime)"""
        query = query_template.format(equity_symbol, expration_date.strftime('%Y-%m-%d'))
        rows = self.select(query)
        #print rows
        start_date = max(datetime.date.today() - datetime.timedelta(days_to_now), rows[0][1])
        filtered_rows = filter(lambda x: x[1] <= start_date, rows)
        #print filtered_rows
        min = sys.maxint
        strik_price = None
        for row in filtered_rows:
            delta = abs(row[0] - current_equity_price)
            if delta < min:
                min = delta
                strik_price = row[0]
        # eg. 'SPY170915C00245000'
        return '%s%sC%08d' % (equity_symbol, expration_date.strftime('%y%m%d'), strik_price * 1000)

    def get_implied_volatilities(self, option_symbol):
        query_template = """select tradeTime, volatility from option_data where symbol = '{}'"""
        query = query_template.format(option_symbol)
        rows = self.select(query)
        return rows

    def get_corresponding_implied_volatilities(self, equity_symbol, current_equity_price):
        exp_date = self.get_following_expirationDate(equity_symbol) #get recent exp_date for this symbol
        option_symbol = self.find_symbol(equity_symbol, exp_date, current_equity_price)
        rows = self.get_implied_volatilities(option_symbol)
        return rows
        #df = pd.DataFrame(rows)
        #df.columns = ['date', 'volatility']
        #return df


if __name__ == '__main__':
    #exp_date = OptionDAO().get_following_expirationDate('SPY')
    #print OptionDAO().find_symbol('SPY', exp_date, 245.38)
    print OptionDAO().get_corresponding_implied_volatilities('SPY', 245.38)


