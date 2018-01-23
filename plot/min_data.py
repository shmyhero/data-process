import datetime
import matplotlib.pyplot as plt
from dataaccess.equityrealtimedao import EquityRealTimeDAO
from dataaccess.equitymindao import EquityMinDAO


def plot_yahoo_equity_line():
    real_data = EquityRealTimeDAO().get_min_time_and_price(datetime.datetime(2018, 1, 19, 9, 30, 0), datetime.datetime(2018, 1, 19, 16, 29, 59))
    min_data = EquityMinDAO().get_time_and_price(datetime.datetime(2018, 1, 19, 9, 31, 0), datetime.datetime(2018, 1, 19, 16, 29, 59))
    time = map(lambda x: x[0], real_data)
    real_values = map(lambda x: x[1], real_data)
    min_values = map(lambda x: x[1], min_data)
    fig, ax = plt.subplots()
    ax.plot(time, min_values)
    ax.plot(time, real_values)
    plt.show()

if __name__ == '__main__':
    plot_yahoo_equity_line()