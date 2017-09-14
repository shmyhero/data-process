import datetime
import pandas as pd
from common.tradetime import TradeTime
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
        return map(lambda x: x[0], rows)
        return map(lambda x: x[0].strftime('%Y-%m-%d'), rows)

    def get_vix_by(self, symbol, date_str, columns):
        select_columns = ', '.join(columns)
        query_template = """select {} from vix where symbol = '{}' and dailyDate1dAgo = str_to_date('{}', '%Y-%m-%d')"""
        query = query_template.format(select_columns, symbol, date_str)
        rows = self.select(query)
        return rows

    def get_following_vix_by_date(self, date_str):
        symbols = VIX.get_following_symbols(date_str)
        columns = ['symbol', 'dailyLastPrice', 'volume']
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
        dates = map(lambda x: x.strftime('%Y-%m-%d'), self.get_all_vix_date())
        records = map(self.get_following_vix_by_date, dates)
        df = pd.DataFrame(records)
        df.columns = ['date', 'f1', 'f2']
        return df

    # not used...
    def get_all_vix(self, columns):
        query_template = """select {} from vix order by dailyDate1dAgo,symbol"""
        select_columns = ', '.join(columns)
        query = query_template.format(select_columns)
        rows = self.select(query)
        return rows

    # not used...
    def get_grouped_all_vix(self):
        columns = ['dailyDate1dAgo', 'symbol', 'dailyLastPrice']
        rows = self.get_all_vix(columns)
        grouped_vix = {}
        records = None
        date = None
        for row in rows:
            if row[0] != date:
                if records is not None:
                    grouped_vix[date] = records
                date = row[0]
                records = []
            records.append(row)
        grouped_vix[date] = records
        return grouped_vix

    def get_vix_price_by_symbol(self, symbol, remove_invalid_date = True):
        query_template = """select dailyDate1dAgo, dailyLastPrice from vix where symbol = '{}' order by dailyDate1dAgo"""
        query = BaseDAO.mysql_format(query_template, symbol)
        rows = self.select(query)
        if remove_invalid_date:
            rows = filter(lambda x: TradeTime.is_trade_day(x[0]), rows)
        df = pd.DataFrame(rows)
        df.columns = ['date', 'price']
        return df

    def get3vix(self, date_str = datetime.datetime.now().strftime('%Y-%m-%d')):
        following_symbols = list(VIX.get_following_symbols(date_str))
        symbols = ['VIY00']
        symbols.extend(following_symbols)
        return map(lambda x: self.get_vix_price_by_symbol(x), symbols)


if __name__ == '__main__':
    #print list(VIXDAO().get_current_and_follwing_vix())
    print VIXDAO().get3vix()

