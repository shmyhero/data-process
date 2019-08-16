import sys
import datetime
import numpy as np
from statsmodels import regression
import statsmodels.api as sm
import matplotlib.pyplot as plt
import talib
from pandas.core import datetools
from dataaccess.yahooequitydao import YahooEquityDAO


def plot_spy_vs_qqq(from_date):
    spy_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date.strftime('%Y-%m-%d'))
    qqq_records = YahooEquityDAO().get_all_equity_price_by_symbol('AMZN', from_date.strftime('%Y-%m-%d'))
    DATE = map(lambda x: x[0], spy_records)
    X = map(lambda x: x[1], spy_records)
    Y = map(lambda x: x[1], qqq_records)
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(DATE, X, 'r-', label='spy')
    # ax2.plot(dates, vix_values1, 'b-', label='vix')
    # ax2.plot(dates, vix_values_mean, 'g-', label='vix')
    ax2.plot(DATE, Y)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()

def linreg(X, Y):
    # Running the linear regression
    X = sm.add_constant(X)
    model = regression.linear_model.OLS(Y, X).fit()
    a = model.params[0]
    b = model.params[1]
    return [a, b]


def plot_spy_vs_qqq_linreg(X, Y, a, b):
    X = sm.add_constant(X)
    X = X[:, 1]
    # Return summary of the regression and plot results
    X2 = np.linspace(X.min(), X.max(), 100)
    Y_hat = X2 * b + a
    plt.scatter(X, Y, alpha=0.3) # Plot the raw data
    plt.plot(X2, Y_hat, 'r', alpha=0.9) # Add the regression line, colored in red
    plt.xlabel('spy')
    plt.ylabel('qqq')
    plt.show()
    #print a, b
    #summary =  model.summary()
    #return summary


def plot_compare_with_predict_X(DATE, X, Y, a, b):
    X2 = map(lambda y: (y - a) / b, Y)
    plt.plot(DATE, X, label = 'SPY')
    plt.plot(DATE, X2, label = 'predict SPY')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=4, borderaxespad=0.)
    plt.show()


def plot_compare_with_predict_Y(DATE, X, Y, a, b):
    Y2 = map(lambda x: x * b + a, X)
    plt.plot(DATE, Y, label = 'QQQ')
    plt.plot(DATE, Y2, label = 'predict QQQ')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=4, borderaxespad=0.)
    plt.show()


def plot_delta(DATE, X, Y, a, b):
    X2 = map(lambda y: (y - a) / b, Y)
    delta_x = map(lambda x,x2: (x-x2)*100/x2, X, X2)
    # plt.plot(DATE, delta_x, label='Delta')
    ma_delta = talib.SMA(np.asarray(delta_x), 30)
    plt.plot(DATE, ma_delta, label='MA Delta')
    ma_delta_long = talib.SMA(np.asarray(delta_x), 60)
    plt.plot(DATE, ma_delta_long, label='MA Delta long')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=4, borderaxespad=0.)
    plt.show()


def plot_linreg(from_date):
    spy_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date.strftime('%Y-%m-%d'))
    qqq_records = YahooEquityDAO().get_all_equity_price_by_symbol('QQQ', from_date.strftime('%Y-%m-%d'))
    DATE = map(lambda x: x[0], spy_records)
    X = map(lambda x: x[1], spy_records)
    Y = map(lambda x: x[1], qqq_records)
    [a, b] = linreg(X, Y)
    print [a, b]
    print 'Correlation: ' + str(np.corrcoef(X, Y)[0, 1])
    # plot_spy_vs_qqq_linreg(X, Y, a, b)
    # plot_compare_with_predict_X(DATE, X, Y, a, b)
    # plot_compare_with_predict_Y(DATE, X, Y, a, b)
    plot_delta(DATE, X, Y, a, b)


if __name__ == '__main__':
    # plot_spy_vs_qqq(datetime.date(2010, 1, 1))
    plot_linreg(datetime.date(2010, 1, 1))
