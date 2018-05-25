import datetime
import pandas as pd
from utils.indicator import MACD
# from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.equity30mindao import Equity30MinDAO
import matplotlib.pyplot as plt


def spy_vs_macd (start_time=datetime.datetime(2007, 1, 1, 0, 0), end_time = datetime.datetime(9999, 1, 1, 0, 0), window=26):
    spy_records = Equity30MinDAO().get_time_and_price('SPY', start_time, end_time)
    spy_prices = map(lambda x: x[1], spy_records)
    macd_list = MACD.get_all_macd(spy_prices, s=7, l=19, m=26)
    dates = map(lambda x: x[0], spy_records)[window:]
    spy_values = map(lambda x: x[1], spy_records)[window:]
    macd_bars = map(lambda x: x[-1], macd_list)[window:]
    macd_rates = map(lambda x, y: x*100/y, macd_bars, spy_values)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    X = range(len(dates))
    ax1.plot(X, spy_values, 'r-', label='spy')
    ax2.plot(X, macd_bars, 'b-', label='macd')
    ax2.plot(X, [0]*len(dates))
    ax1.grid()
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()


if __name__ == '__main__':
    spy_vs_macd(datetime.datetime(2007, 1, 1, 0, 0, 0), datetime.datetime(2008, 1, 1, 0, 0, 0))