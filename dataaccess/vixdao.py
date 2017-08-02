import pandas as pd
from entities.vix import VIX
from dataaccess.basedao import BaseDAO


class VIXDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into vix (symbol,lastPrice,priceChange,openPrice,highPrice,lowPrice,previousPrice,volume,tradeTime,dailyLastPrice,dailyPriceChange,dailyOpenPrice,dailyHighPrice,dailyLowPrice,dailyPreviousPrice,dailyVolume,dailyDate1dAgo) values ('{}',{},{},{},{},{},{},{},'{}',{},{},{},{},{},{},{},'{}')"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        count = 0
        for vix in records:
            query = BaseDAO.mysql_format(query_template, vix.symbol, vix.lastPrice, vix.priceChange, vix.openPrice, vix.highPrice, vix.lowPrice, vix.previousPrice, vix.volume, vix.tradeTime, vix.dailyLastPrice, vix.dailyPriceChange, vix.dailyOpenPrice, vix.dailyHighPrice, vix.dailyLowPrice, vix.dailyPreviousPrice, vix.dailyVolume, vix.dailyDate1dAgo)
            self.execute_query(query, cursor)
            count += 1
            if count == 1000:
                conn.commit()
                count = 0
        conn.commit()
        conn.close()

    def get_all_vix_date(self):
        query = """select distinct dailyDate1dAgo from vix order by dailyDate1dAgo"""
        rows = self.select(query)
        return map(lambda x: x[0].strftime('%Y-%m-%d'), rows)


    def get_vix_by(self, symbol, date_str, columns):
        select_columns = ', '.join(columns)
        query_template = """select {} from vix where symbol = '{}' and dailyDate1dAgo = str_to_date('{}', '%Y-%m-%d')"""
        query = query_template.format(select_columns, symbol, date_str)
        rows = self.select(query)
        return rows

    def get_following_vix_by_date(self, date_str):
        symbols = list(VIX.get_following_symbols(date_str))
        columns = ['symbol', 'lastPrice', 'volume']
        records = []
        for symbol in symbols:
            rows = self.get_vix_by(symbol, date_str, columns)
            if len(rows) > 0:
                records.extend(rows)
            if len(records) == 2:
                break
        #return records
        return [date_str, records[0][1], records[1][1]]

    # notice: the performance can be improved if get all vix the data from database once.
    def gen_all_vix(self):
        dates = self.get_all_vix_date()
        records = map(self.get_following_vix_by_date, dates)
        df = pd.DataFrame(records)
        df.columns = ['date', 'f1', 'f2']
        return df



if __name__ == '__main__':
    print VIXDAO().gen_all_vix()

