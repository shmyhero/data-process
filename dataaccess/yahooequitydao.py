import numpy as np
import pandas as pd
import datetime
from dataaccess.basedao import BaseDAO
from utils.maths import get_sharp_ratio
from common.symbols import Symbols
from common.pathmgr import PathMgr
from common.tradetime import TradeTime
from common.optioncalculater import OptionCalculater


class YahooEquityDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def get_equity_price_by_date(self, symbol, date_str, price_field = 'closePrice', cursor=None):
        """
        :param symbol:
        :param date_str: the format is 'YYYY-mm-dd'
        :param price_field:
        :return: price
        """
        query_template = """select {} from yahoo_equity where symbol = '{}' and tradeDate <= str_to_date('{}', '%Y-%m-%d') order by tradeDate desc limit 1"""
        query = query_template.format(price_field, symbol, date_str)
        rows = self.select(query, cursor)
        if rows is None or len(rows) < 1:
            return None
        else:
            return rows[0][0]

    def get_all_equity_price_by_symbol(self, symbol, from_date_str='1993-01-01', price_field = 'adjClosePrice'):
        query_template = """select tradeDate, {} from yahoo_equity where symbol = '{}' and tradeDate >= str_to_date('{}', '%Y-%m-%d') order by tradeDate"""
        query = query_template.format(price_field, symbol, from_date_str)
        rows = self.select(query)
        return rows

    def get_equity_monthly_by_symbol(self, symbol, columns):
        """
        :param symbol: eg: SPY
        :return: rows
        """
        columns_sql = ', '.join(columns)
        query_template = """select {} from yahoo_equity_monthly_view where symbol = '{}'"""
        query = query_template.format(columns_sql, symbol)
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df

    def get_latest_price(self, symbol):
        query_template = """select closePrice from yahoo_equity where symbol = '{}' order by tradeDate desc limit 1"""
        query = query_template.format(symbol)
        rows = self.select(query)
        return rows[0][0]

    def insert(self, symbol, df):
        query_template = """insert into yahoo_equity (symbol,tradeDate,openPrice,highPrice,lowPrice,closePrice,adjClosePrice,volume) values ('{}','{}',{},{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            if TradeTime.is_trade_day(datetime.datetime.strptime(row['Date'], '%Y-%m-%d')):
                query = BaseDAO.mysql_format(query_template, symbol, row['Date'], row['Open'], row['High'],
                                            row['Low'], row['Close'], row['Adj Close'], row['Volume'])
                self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def insert_all(self):
        for symbol in Symbols.get_all_symbols():
            self.logger.info('insert data for %s...' %symbol)
            path = PathMgr.get_historical_etf_path(symbol)
            df = pd.read_csv(path)
            self.insert(symbol, df)

    def save(self, symbol, df):
        query_template = """insert into yahoo_equity (symbol,tradeDate,openPrice,highPrice,lowPrice,closePrice,adjClosePrice,volume) values 
                           ('{}','{}',{},{},{},{},{},{}) on duplicate key update adjClosePrice = {}"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()

        for index, row in df.iterrows():
            if TradeTime.is_trade_day(datetime.datetime.strptime(row['Date'], '%Y-%m-%d')):
                query = BaseDAO.mysql_format(query_template, symbol, row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume'], row['Adj Close'])
                #print query
                self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def save_from_equities(self, equities):
        query_template = """insert into yahoo_equity (symbol,tradeDate,openPrice,highPrice,lowPrice,closePrice,adjClosePrice,volume) values 
                                   ('{}','{}',{},{},{},{},{},{}) on duplicate key update 
                                   openPrice={},highPrice={},lowPrice={},closePrice={},adjClosePrice={},volume={}"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()

        for equity in equities:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.lastPrice, equity.volume, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.lastPrice, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()


    def save_all(self, symbols = Symbols.get_all_symbols()):
        for symbol in symbols:
            self.logger.info('save data for %s...' %symbol)
            path = PathMgr.get_historical_etf_path(symbol)
            df = pd.read_csv(path)
            self.save(symbol, df)

    def get_last_trade_day_symbols(self):
        date = TradeTime.get_latest_trade_date()
        query = """select symbol from yahoo_equity where tradeDate = '{}'""".format(date)
        rows = self.select(query)
        return map(lambda row: row[0], rows)

    def get_start_date_by_symbol(self, symbol, cursor):
        query = """select tradeDate from yahoo_equity where symbol = '{}' order by tradeDate limit 1 """.format(symbol)
        rows = self.select(query, cursor)
        return rows[0][0]

    def get_end_date_by_symbol(self, symbol, cursor):
        query = """select tradeDate from yahoo_equity where symbol = '{}' order by tradeDate desc limit 1 """.format(symbol)
        rows = self.select(query, cursor)
        return rows[0][0]

    def get_start_end_date_by_symbols(self):
        reversed_yahoo_symbol_mapping = Symbols.get_reversed_yahoo_symbol_mapping()
        conn = self.get_connection()
        cursor = conn.cursor()
        records = []
        for symbol in Symbols.get_all_symbols():
            start_date = self.get_start_date_by_symbol(symbol, cursor)
            end_date = self.get_end_date_by_symbol(symbol, cursor)
            records.append([Symbols.get_mapped_symbol(symbol,reversed_yahoo_symbol_mapping), start_date, end_date])
            records.sort()
        conn.close()
        return records

    def get_missing_records_symbols(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        missing_symbols = []
        last_trade_date = TradeTime.get_latest_trade_date()
        for symbol in Symbols.get_all_symbols():
            end_date = self.get_end_date_by_symbol(symbol, cursor)
            if end_date < last_trade_date:
                missing_symbols.append(symbol)
        conn.close()
        return missing_symbols

    def filter_liquidity_symbols(self, current_date=None, window=30, count=50, ignore_symbols = ['BIL', 'IEF', 'XIV']):
        if current_date is None:
            current_date = TradeTime.get_latest_trade_date()
        from_date = TradeTime.get_from_date_by_window(window, current_date)
        ignore_symbols_sql = ','.join(map(lambda x: '\'%s\''%x, ignore_symbols))
        sql_template = """SELECT symbol, avg(adjClosePrice * volume) as liquidity FROM tradehero.yahoo_equity where tradeDate > '{}' and tradeDate <='{}'  and symbol not like '^%' and symbol not like '%.SS' and symbol not in ({}) group by symbol order by liquidity desc;"""
        sql = sql_template.format(from_date, current_date, ignore_symbols_sql)
        rows = self.select(sql)
        return map(lambda x: x[0], rows[:count])

    def get_monthly_diff_price_by_symbol(self, symbol, cursor = None, window = 36):
        query_template = """select lastDate, adjClosePrice from yahoo_equity_monthly_view where symbol = '{}' order by lastDate desc limit {}"""
        query = query_template.format(symbol, window)
        rows = self.select(query, cursor)
        a = np.array(map(lambda x: x[1], reversed(rows)))
        # ignore the last one because of the last price is current date rather than the end of month?
        # return np.diff(np.log(a))[:-1]
        return np.diff(np.log(a))

    def get_all_monthly_diff_price_by_symbols(self, symbols, window = 36, end_date = datetime.date(9999, 12, 12)):
        query_template = """select symbol, lastDate, adjClosePrice from yahoo_equity_monthly_view where symbol in ({}) and lastDate < '{}' order by lastDate desc limit {}"""
        symbols_sql = ','.join(map(lambda x: '\'%s\'' % x, symbols))
        query = query_template.format(symbols_sql, end_date, window*len(symbols))
        # print query
        rows = self.select(query)
        diffs = []
        for symbol in symbols:
            symbol_rows = filter(lambda x: x[0] == symbol, rows)
            symbol_rows.sort(key=lambda x: x[1])
            a = np.array(map(lambda x: x[2], symbol_rows))
            diff = np.diff(a)
            diffs.append(diff)
        return diffs

    def get_symbol_volatilities(self, symbols, window=120, end_date=datetime.date(9999, 12, 12)):
        query_template = """select symbol, tradeDate, adjClosePrice from yahoo_equity where symbol in ({}) and tradeDate < '{}' and adjClosePrice is not null order by tradeDate desc limit {}"""
        symbols_sql = ','.join(map(lambda x: '\'%s\'' % x, symbols))
        query = query_template.format(symbols_sql, end_date, window * len(symbols))
        # print query
        rows = self.select(query)
        volatitilies = []
        for symbol in symbols:
            # print symbol
            symbol_rows = filter(lambda x: x[0] == symbol, rows)
            symbol_rows.sort(key=lambda x: x[1])
            price_list = map(lambda x: x[2], symbol_rows)
            # print price_list
            volatitily = OptionCalculater.get_history_volatility2(price_list)
            volatitilies.append([symbol, volatitily])
        return volatitilies

    def get_symbol_sharp_ratio(self, symbols, window=120, end_date=datetime.date(9999, 12, 12)):
        query_template = """select symbol, tradeDate, adjClosePrice from yahoo_equity where symbol in ({}) and tradeDate < '{}' and adjClosePrice is not null order by tradeDate desc limit {}"""
        symbols_sql = ','.join(map(lambda x: '\'%s\'' % x, symbols))
        query = query_template.format(symbols_sql, end_date, window * len(symbols))
        # print query
        rows = self.select(query)
        sharp_ratios = []
        for symbol in symbols:
            # print symbol
            symbol_rows = filter(lambda x: x[0] == symbol, rows)
            symbol_rows.sort(key=lambda x: x[1])
            price_list = map(lambda x: x[2], symbol_rows)
            # print price_list
            sharp_ratio = get_sharp_ratio(price_list)
            sharp_ratios.append([symbol, sharp_ratio])
        return sharp_ratios

    def get_lack_of_liquity_symbols(self, window=100):
        from dateutil.relativedelta import relativedelta
        result = []
        today = datetime.date.today()
        current = datetime.date(2011, 1, 1)
        tradable_symbols = Symbols.get_all_tradeable_symbols()
        set_symbols = set(['BIL', 'IEF', 'XIV', 'VIX', 'GLD', 'SLV', 'TLT', 'ZIV'])
        while current <= today:
            result.append(current)
            current += relativedelta(months=1)
        for date in result:
            print date
            symbols = self.filter_liquidity_symbols(date, window=window)
            set_symbols = set_symbols.union(set(symbols))
        # print 'set_symbols = %s'%set_symbols
        return filter(lambda x: x not in set_symbols, tradable_symbols)

        # symbols = self.filter_liquidity_symbols(datetime.date(2018, 1, 1), window=window)
        # tradable_symbols = Symbols.get_all_tradeable_symbols()
        # return filter(lambda x: x not in symbols, tradable_symbols)




if __name__ == '__main__':
    # YahooEquityDAO().save_all(['^GSPC'])
    # YahooEquityDAO().save_all(['^GSPC', '^DJI'])
    # YahooEquityDAO().save_all(['^VXV'])
    # YahooEquityDAO().save_all(['^VXMT'])
    # YahooEquityDAO().save_all(['VNM'])
    # YahooEquityDAO().save_all(['ITA', 'XAR', 'FNDE', 'DGRW', 'IHI', 'BJK', 'VHT', 'CME'])
    # YahooEquityDAO().save_all(['XIV'])
    # YahooEquityDAO().save_all(['STZ'])
    # YahooEquityDAO().save_all(['AAPL'])
    # print YahooEquityDAO().get_latest_price('SPY')
    # print YahooEquityDAO().get_equity_price_by_date('SPY', '2017-08-05')
    # print YahooEquityDAO().get_equity_monthly_by_symbol('SPY', ['symbol', 'lastdate', 'closeprice', 'adjcloseprice', 'tradeyear', 'trademonth'])
    # print YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str='2017-08-01')
    # print YahooEquityDAO().get_last_trade_day_symbols()
    # print YahooEquityDAO().get_start_end_date_by_symbols()
    # YahooEquityDAO().save_all(['ADBE', 'AVGO', 'AMZN', 'NFLX', 'GOOG'])
    # YahooEquityDAO().save_all(['000001.SS'])
    # print YahooEquityDAO().get_equity_monthly_by_symbol('000001.SS', ['closePrice'])
    # YahooEquityDAO().save_all(['AIEQ'])
    YahooEquityDAO().save_all(['SPY'])
    # print YahooEquityDAO().filter_liquidity_symbols(datetime.date(2018, 1, 1))
    # print YahooEquityDAO().get_monthly_diff_price_by_symbol('SPY')
    # symbols = YahooEquityDAO().filter_liquidity_symbols(current_date=datetime.date(2018, 1, 31))
    # print symbols
    # symbols = ['XLF', 'GLD', 'XLE', 'XLU', 'V', 'AVGO', 'BRK-B', 'XLK', 'EWZ', 'XLI', 'GDX', 'SVXY', 'LQD', 'VOO', 'FXI', 'XLV', 'VWO', 'XOP', 'XLP', 'EWJ', 'IYR', 'STZ', 'MO', 'MA', 'JNK', 'ADBE', 'XLY', 'AGG', 'XBI', 'GDXJ', 'LMT', 'VNQ', 'SMH', 'MDY', 'KRE', 'XLB']
    # print YahooEquityDAO().get_symbol_volatilities(symbols, end_date=datetime.date(2018, 1, 31))
    # YahooEquityDAO().save_all(['MSFT'])
    # print YahooEquityDAO().get_lack_of_liquity_symbols(200)
    # print YahooEquityDAO().get_symbol_sharp_ratio(symbols, end_date=datetime.date(2018, 1, 31))