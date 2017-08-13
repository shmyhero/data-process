
import datetime
import matplotlib.pyplot as plt
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahooequitydao import YahooEquityDAO

def plot_lines(credits_df, spy_df):
    #print credits_df
    dates = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), credits_df['lastDate'])
    debt = credits_df['margin_debt']
    spy_prices = spy_df['adjcloseprice'][0:len(dates)]
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(dates, debt, 'r-', label='credit margin debt')
    ax2.plot(dates, spy_prices, 'b-', label='SPY')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()


if __name__ == '__main__':
    credits_df = NYSECreditDAO().get_all_margin_debt()
    #date_str_list = map(lambda x: x.date_str, credits)
    spy_df = YahooEquityDAO().get_equity_monthly_by_symbol('SPY', ['lastdate','adjcloseprice'])
    plot_lines(credits_df, spy_df)
