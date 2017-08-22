import datetime
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

    def get_following_expirationDate(self, symbol, from_date_str=datetime.datetime.today().strftime('%Y-%m-%d')):
        query_template = """select distinct(expirationDate) from  option_data 
                            where underlingSymbol = '{}' and expirationDate >= str_to_date('{}', '%Y-%m-%d')
                            order by expirationDate"""
        query = query_template.format(symbol, from_date_str)
        rows = self.select(query)
        for row in rows:
            d = row[0]
            if d.weekday() == 4 and 14 < d.day < 22:
                return d

    #TODO:test it.
    def find_symbol(self, symbol, expration_date, current_equity_price):
        query_template = """select distinct(strikeprice) from  option_data where underlingSymbol = '{}'  and  expirationDate =  str_to_date('{}', '%Y-%m-%d') and optionType = 'Call' """
        query = query_template.format(symbol, expration_date.strftime('%Y-%m-%d'))
        rows = self.select(query)
        min = 99999999
        strik_price = None
        for row in rows:
            delta = abs(row[0] - current_equity_price)
            if delta < min:
                min = delta
                strik_price = row[0]
        #'SPY170915C00245000'
        return '%s%sC%08d' % (symbol, expration_date.strftime('%y%m%d'), strik_price * 1000)


if __name__ == '__main__':
    print OptionDAO().get_following_expirationDate('SPY')


