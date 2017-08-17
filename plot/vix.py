import datetime
import matplotlib.pyplot as plt
from dataaccess.vixdao import VIXDAO


def plot_vix(df, label):
    dates = df['date']
    price = df['price']
    fig, ax = plt.subplots()
    ax.plot(dates, price, label=label)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()

def plot_vix_3in1():
    dfs = VIXDAO().get3vix()
    dates = dfs[0]['date']
    price_index = dfs[0]['price']
    price_f1 = dfs[1]['price']
    price_f2 = dfs[2]['price']
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