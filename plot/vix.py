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

if __name__ == '__main__':
    dfs = VIXDAO().get3vix()
    plot_vix(dfs[0], 'index')
    plot_vix(dfs[1], 'f1')
    plot_vix(dfs[2], 'f2')