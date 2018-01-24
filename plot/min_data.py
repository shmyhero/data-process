import datetime
import matplotlib.pyplot as plt
from dataaccess.equityrealtimedao import EquityRealTimeDAO
from dataaccess.equitymindao import EquityMinDAO


def plot_yahoo_equity_line():
    real_data = EquityRealTimeDAO().get_min_time_and_price('XIV', datetime.datetime(2018, 1, 23, 9, 30, 0), datetime.datetime(2018, 1, 23, 16, 30, 0))
    min_data = EquityMinDAO().get_time_and_price('XIV', datetime.datetime(2018, 1, 23, 9, 30, 0), datetime.datetime(2018, 1, 23, 16, 30, 0))
    time = map(lambda x: x[0], real_data)
    real_values = map(lambda x: x[1], real_data)
    min_values = map(lambda x: x[1], min_data)
    fig, ax = plt.subplots()
    ax.plot(time, min_values, label='min')
    ax.plot(time, real_values, label='real')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()

if __name__ == '__main__':
    plot_yahoo_equity_line()