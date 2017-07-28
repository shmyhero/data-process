import pandas as pd
from dataaccess.basedao import BaseDAO


class EquityDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into equity (symbol,tradeTime,openPrice,highPrice,lowPrice,lastPrice,priceChange,volume) values ('{}','{}',{},{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        for equity in records:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.priceChange, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def select_by_symbols(self, symbols):
        columns = ['symbol', 'tradeTime', 'openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'priceChange', 'volume']
        fields = ', '.join(columns)
        symbols_sql = ', '.join(map(lambda x: '\'%s\''%x, symbols))
        query_template = """select {} from equity where symbol in ({})"""
        query = query_template.format(fields, symbols_sql)
        print query
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df

    def get_price_change_percentage(self, from_date, to_date):

        query_template = """select t1.symbol, (t2.end_price - t1.start_price)/t1.start_price as percentage from 
                        (select symbol, lastPrice as start_price from equity where tradeTime = str_to_date('2017-07-24', '%Y-%m-%d')) as t1,
                        (select symbol, lastPrice as end_price from equity where tradeTime = str_to_date('2017-07-26', '%Y-%m-%d')) as t2
                        where t1.symbol = t2.symbol order by percentage desc"""
        query = query_template.format(from_date, to_date)
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = ['symbol', 'price_change_percentage']
        return df


if __name__ == '__main__':
    df = EquityDAO().get_price_change_percentage('2017-07-24', '2017-07-26')
    print df
    #df_left =
    #print df[df.symbol.any(['IXC', 'IXP', 'UNG', 'IDU', 'GLD'])]
