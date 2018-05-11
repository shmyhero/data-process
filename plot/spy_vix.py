import datetime
import pandas as pd
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.vixdao import VIXDAO
import matplotlib.pyplot as plt


def spy_vs_vix (from_date, ma_window=10):
    spy_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date.strftime('%Y-%m-%d'))
    vix_records = YahooEquityDAO().get_all_equity_price_by_symbol('^VIX', from_date.strftime('%Y-%m-%d'))
    dates = map(lambda x: x[0], spy_records)[ma_window*3:]
    spy_values = map(lambda x: x[1], spy_records)[ma_window*3:]
    vix_values = map(lambda x: x[1], vix_records)
    vix_values1 = pd.Series(vix_values).rolling(window=ma_window).mean().tolist()[ma_window*3:]
    vix_values_mean = pd.Series(vix_values).rolling(window=ma_window*3).mean().tolist()[ma_window*3:]
    value = 13
    buy_or_hold = map(lambda x,y: 0 if x>value or y > value else 1, vix_values1, vix_values_mean)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(dates, spy_values, 'r-', label='spy')
    # ax2.plot(dates, vix_values1, 'b-', label='vix')
    # ax2.plot(dates, vix_values_mean, 'g-', label='vix')
    ax2.plot(dates, buy_or_hold)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()

if __name__ == '__main__':
    spy_vs_vix(datetime.date(2010, 1, 1,))
