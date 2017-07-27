import pandas as pd
import datetime
import matplotlib.pyplot as plt
from dataaccess.optionskewdao import OptionSkewDAO


class Skew(object):

    def __init__(self):
        pass

    def plot_lines(self, symbol):
        df = OptionSkewDAO().select_by_symbol(symbol)
        fig, ax1 = plt.subplots()
        x = df['tradeTime']
        y1 = df['price']
        y2 = df['skew']

        ax2 = ax1.twinx()
        ax1.plot(x, y1, 'g-')
        ax2.plot(x, y2, 'b-')

        lines, labels = ax1.get_legend_handles_labels()
        ax1.legend(lines[:2], labels[:2])
        plt.show()


if __name__ == '__main__':
    Skew().plot_lines('SPY')
