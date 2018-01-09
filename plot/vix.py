import datetime
import matplotlib.pyplot as plt
from dataaccess.vixdao import VIXDAO
from common.tradetime import TradeTime

def plot_vix(df, label):
    dates = df['date']
    price = df['price']
    fig, ax = plt.subplots()
    ax.plot(dates, price, label=label)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()

def plot_vix_3in1():
    from_date = TradeTime.get_latest_trade_date() - datetime.timedelta(50)
    records_index = VIXDAO().get_vix_price_by_symbol_and_date('VIY00', from_date = from_date)
    dates = map(lambda x: x[0], records_index)
    price_index = map(lambda x: x[1], records_index)
    (records_f1, records_f2, records_f3) = VIXDAO().get_following_vix(from_date)
    price_f1 = map(lambda x: x[1], records_f1)
    price_f2 = map(lambda x: x[1], records_f2)
    fig, ax = plt.subplots()
    ax.plot(dates, price_index, label='index')
    ax.plot(dates, price_f1, label='f1')
    ax.plot(dates, price_f2, label='f2')
    plt.grid()
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()


if __name__ == '__main__':
    plot_vix_3in1()
    #dfs = VIXDAO().get3vix()
    #plot_vix(dfs[0], 'index')
    #plot_vix(dfs[1], 'f1')
    #plot_vix(dfs[2], 'f2')