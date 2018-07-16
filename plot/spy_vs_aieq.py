
import datetime
import matplotlib.pyplot as plt
from dataaccess.yahooequitydao import YahooEquityDAO

def plot_spy_vs_aieq(from_date=datetime.date(2017, 1, 1)):
    spy_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date.strftime('%Y-%m-%d'))
    aieq_records = YahooEquityDAO().get_all_equity_price_by_symbol('AIEQ', from_date.strftime('%Y-%m-%d'))
    dates = map(lambda x: x[0], aieq_records)
    spy_values = map(lambda x: x[1], spy_records[-len(dates):])
    aieq_values = map(lambda x: x[1], aieq_records)
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(dates, spy_values, 'r-', label='spy')
    ax2.plot(dates, aieq_values, 'b-', label='aieq')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()

if __name__ == '__main__':
    plot_spy_vs_aieq()