import matplotlib.pyplot as plt
from dataaccess.yahooequitydao import YahooEquityDAO


class DayNightDelta(object):

    def __init__(self):
        [self.dates, self.spy_prices, self.days_delta, self.night_delta] = self.load_spy_records()

    def load_spy_records(self):
        rows = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str='1993-01-01', price_field='openPrice, closePrice')
        dates =map(lambda x:x[0],rows)
        spy_prices = map(lambda x: x[2], rows)
        days_delta = []
        night_delta = []
        for i in range(len(rows)):
            days_delta.append(rows[i][2]-rows[i][1])
            if i == 0:
                night_delta.append(0)
            else:
                night_delta.append(rows[i][1] - rows[i-1][2])
        return [dates, spy_prices, days_delta, night_delta]

    def plot_delta(self):
        fig, ax = plt.subplots()
        ax.plot(self.dates, self.days_delta, label='days_delta')
        ax.plot(self.dates, self.night_delta, label='night_delta')
        # plt.grid()
        plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
        plt.show()

    def plot_delta_sum(self):
        days_delta_sum_list = []
        night_delta_sum_list = []
        day_sum = 0
        night_sum = 0
        for i in range(len(self.dates)):
            day_sum += self.days_delta[i]
            days_delta_sum_list.append(day_sum)
            night_sum += self.night_delta[i]
            night_delta_sum_list.append(night_sum)
        fig, ax = plt.subplots()
        ax.plot(self.dates, days_delta_sum_list, label='days_delta_sum')
        ax.plot(self.dates, night_delta_sum_list, label='night_delta_sum')
        # plt.grid()
        plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
        plt.show()

    def plot_delta_of_delta_sum(self):
        delta_of_delta_list = []
        sum = 0
        for i in range(len(self.dates)):
            sum += self.night_delta[i]-self.days_delta[i]
            delta_of_delta_list.append(sum)
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(self.dates, delta_of_delta_list, 'r-', label='delta of delta')
        ax2.plot(self.dates, self.spy_prices, 'b-', label='SPY')

        plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
        plt.show()

if __name__ == '__main__':
    # print DayNightDelta().plot_delta()
    # print DayNightDelta().plot_delta_sum()
    print DayNightDelta().plot_delta_of_delta_sum()