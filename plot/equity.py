import pandas as pd
import datetime
import matplotlib.pyplot as plt
from dataaccess.optionskewdao import OptionSkewDAO
from dataaccess.equitydao import EquityDAO
from dataaccess.yahooequitydao import YahooEquityDAO


class Equity(object):

    def __init__(self):
        pass

    @staticmethod
    def plot_equity_lines(symbols):
        df = EquityDAO().select_by_symbols(symbols)
        print df
        fig, ax = plt.subplots()
        x = None
        for the_symbol in symbols:
            sub_df = df[df.symbol == the_symbol]
            x = sub_df['tradeTime']
            y = sub_df['lastPrice']
            ax.plot(x, y)
        plt.show()

    @staticmethod
    def plot_yahoo_equity_line(symbol):
        spy_records = YahooEquityDAO().get_all_equity_price_by_symbol(symbol)
        dates = map(lambda x: x[0], spy_records)
        spy_values = map(lambda x: x[1], spy_records)
        fig, ax = plt.subplots()
        ax.plot(dates, spy_values)
        plt.show()

if __name__ == '__main__':
    #Equity.plot_equity_lines(['SPY'])
    Equity.plot_yahoo_equity_line('SPY')


