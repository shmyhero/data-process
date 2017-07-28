import pandas as pd
import datetime
import matplotlib.pyplot as plt
from dataaccess.optionskewdao import OptionSkewDAO
from dataaccess.equitydao import EquityDAO

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



if __name__ == '__main__':
    Equity.plot_equity_lines(['SPY'])


