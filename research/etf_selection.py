import datetime
import pandas as pd
from utils.stringhelper import byteify
from common.symbols import Symbols
from dataaccess.yahooequitydao import YahooEquityDAO


class ETFSelection(object):

    def __init__(self):
        self.yahoo_dao = YahooEquityDAO()
        self.ignore_symbols = ['BIL', 'IEF', 'XIV', 'VIX', 'GLD', 'SLV', 'TLT', 'ZIV']

    @staticmethod
    def get_combinations(lst):
        combinations = []
        length = len(lst)
        for i in range(length - 1):
            j = i + 1
            while i < j:
                if j == length:
                    break
                else:
                    combinations.append([lst[i], lst[j]])
                    j += 1
        return combinations


    def get_correlation_coefficient(self, diff1, diff2):
        correlation_coefficient = pd.Series(diff1).corr(pd.Series(diff2))
        return correlation_coefficient
        # correlation coefficient sample
        # a = [1, 2, 3, 4 , 5]
        # b = [2, 4, 6 ,8, 10]
        # pd.Series(a).corr(pd.Series(b))

    def get_low_volatility_symbols(self, current_date=None, window = 120, liquidity_filter_count = 50, vol_filter_count=30):
        symbols = self.yahoo_dao.filter_liquidity_symbols(count=liquidity_filter_count, ignore_symbols=self.ignore_symbols)
        symbol_volatilities = self.yahoo_dao.get_symbol_volatilities(symbols, window, current_date)
        symbol_volatilities.sort(key=lambda x: x[1])
        return map(lambda x: x[0], symbol_volatilities[:vol_filter_count])

    # obsoleted
    def get_all_corr_dic(self):
        symbols = self.yahoo_dao.filter_liquidity_symbols(count=50)
        # conn = self.yahoo_dao.get_connection()
        # cursor = conn.cursor()
        # diffs = map(lambda x: self.yahoo_dao.get_monthly_diff_price_by_symbol(x, cursor), symbols)
        diffs = self.yahoo_dao.get_all_monthly_diff_price_by_symbols(symbols)
        symbols_pair_list = ETFSelection.get_combinations(symbols)
        diffs_pair_list = ETFSelection.get_combinations(diffs)
        corr_dic = {}
        for i in range(len(symbols_pair_list)):
            [s1, s2] = symbols_pair_list[i]
            [diff1, diff2] = diffs_pair_list[i]
            key = '%s-%s' % (s1, s2)
            reverse_key = '%s-%s' % (s2, s1)
            corr = self.get_correlation_coefficient(diff1, diff2)
            corr_dic[key] = corr
            corr_dic[reverse_key] = corr
        return corr_dic

    def get_all_corr(self, current_date=None, liquidity_filter_count=30, volatility_filter_count=None):
        if volatility_filter_count is not None:
            symbols = self.get_low_volatility_symbols(current_date=current_date, liquidity_filter_count=liquidity_filter_count, vol_filter_count=volatility_filter_count)
        else:
            symbols = self.yahoo_dao.filter_liquidity_symbols(current_date=current_date, count=liquidity_filter_count, ignore_symbols=self.ignore_symbols)
        diffs = self.yahoo_dao.get_all_monthly_diff_price_by_symbols(symbols, end_date=current_date)
        df = None
        for i in range(len(symbols)):
            new_df = pd.DataFrame({symbols[i]: diffs[i]})
            if df is None:
                df = new_df
            else:
                df = df.join(new_df)
        # print df
        correlation_coefficient = df.corr()
        return correlation_coefficient

    def get_low_corr_symbols(self, current_date=None, count=8, liquidity_filter_count=30, volatility_filter_count=None):
        df = self.get_all_corr(current_date,  liquidity_filter_count=liquidity_filter_count, volatility_filter_count=volatility_filter_count)
        corr_sum = df[df.columns].sum() - 1
        # print corr_sum
        records = map(lambda x,y: [x, y], corr_sum.index, corr_sum.tolist())
        records = filter(lambda x: x[1] > 0, records)
        records.sort(key=lambda x: x[1])
        # corr_sum.sort_vaues(assending=False)
        return map(lambda x: x[0], records[:count])

    def get_monthly_end_date(self, start_date=datetime.date(2011, 1, 1)):
        df = self.yahoo_dao.get_equity_monthly_by_symbol('SPY', ['lastDate'])
        dates = df['lastDate'].values.tolist()
        dates = filter(lambda x: x > start_date, dates)
        return dates

    def get_monthly_symbols(self, start_date=datetime.date(2011, 1, 1), liquidity_filter_count=50, volatility_filter_count=None):
        results = {}
        for date in self.get_monthly_end_date(start_date):
            symbols = self.get_low_corr_symbols(date, liquidity_filter_count=liquidity_filter_count, volatility_filter_count=volatility_filter_count)
            results[date] = map(byteify, symbols)
        return results

    @staticmethod
    def get_symbols_mapping():
        symbols = Symbols.get_all_tradeable_symbols()
        items = map(lambda x: '\'%s\':symbol(\'%s\')'%(x, x), symbols)
        return '{%s}'%','.join(items)


if __name__ == '__main__':
    # dic = ETFSelection().get_all_corr_dic()
    # print dic
    # df = ETFSelection().get_all_corr()
    # print df
    # symbols = ETFSelection().get_low_corr_symbols(datetime.date(2015, 1, 1))
    # print symbols
    # print ETFSelection().get_monthly_end_date()
    # print ETFSelection().get_monthly_symbols(liquidity_filter_count=50, volatility_filter_count=None)
    # print ETFSelection().get_monthly_symbols()
    # print ETFSelection.get_symbols_mapping()
    # print ETFSelection().get_low_volatility_symbols()
    print ETFSelection().get_monthly_symbols(liquidity_filter_count=50, volatility_filter_count=35)