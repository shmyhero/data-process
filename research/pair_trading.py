import pandas as pd
import numpy as np
from dataaccess.yahooequitydao import YahooEquityDAO
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt


class PairTrading(object):

    def __init__(self):
        self.yahoo_dao = YahooEquityDAO()

    def show_ratio(self, equity1, equity2):
        records1 = self.yahoo_dao.get_all_equity_price_by_symbol(equity1, from_date_str='2008-01-01')
        records2 = self.yahoo_dao.get_all_equity_price_by_symbol(equity2, from_date_str='2008-01-01')
        dates = map(lambda x: x[0], records1)
        prices1 = map(lambda x: x[1], records1)
        prices2 = map(lambda x: x[1], records2)
        score, pvalue, _ = coint(prices1, prices2)
        print(pvalue)
        ratios = map(lambda x, y: x/y, prices1, prices2)
        # ratios = prices1/prices2
        fig, ax = plt.subplots()
        ax.plot(dates, ratios)
        plt.axhline(np.average(ratios))
        plt.show()

    # def zscore(series):
    #     return (series - series.mean()) / np.std(series)

    @staticmethod
    def zscore(lst):
        ave = np.average(lst)
        std = np.std(lst)
        return map(lambda x: (x-ave)/std, lst)
    

if __name__ == '__main__':
    PairTrading().show_ratio('ADBE', 'MSFT')
