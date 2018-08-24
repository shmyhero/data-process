import pandas as pd
from dataaccess.yahooequitydao import YahooEquityDAO


class ETFSelection(object):

    def __init__(self):
        self.yahoo_dao = YahooEquityDAO()

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

    def get_all_corr_dic(self):
        symbols = self.yahoo_dao.filter_liquidity_symbols()
        conn = self.yahoo_dao.get_connection()
        cursor = conn.cursor()
        diffs = map(lambda x: self.yahoo_dao.get_monthly_diff_price_by_symbol(x, cursor), symbols)
        symbols_pair_list = ETFSelection.get_combinations(symbols)
        diffs_pair_list = ETFSelection.get_combinations(diffs)
        corr_dic = {}
        for i in range(len(symbols_pair_list)):
            [s1, s2] = symbols_pair_list[i]
            [diff1, diff2] = diffs_pair_list[i]
            key = '%s-%s' % (s1, s2)
            reverse_key = '%s-%s'%(s2, s1)
            corr = self.get_correlation_coefficient(diff1, diff2)
            corr_dic[key] = corr
            corr_dic[reverse_key] = corr
        return corr_dic


if __name__ == '__main__':
    dic = ETFSelection().get_all_corr_dic()
    print dic