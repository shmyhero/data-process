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

