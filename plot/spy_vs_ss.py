
import datetime
import matplotlib.pyplot as plt
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.nysecreditdao import NYSECreditDAO

def plot_lines(credits_df, spy_df, ss_df):
    dates = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), credits_df['lastDate'])
    # debt = credits_df['adjcloseprice']
    spy_prices = spy_df['adjcloseprice'][0:len(dates)]
    ss_prices = ss_df['adjcloseprice'][0:len(dates)]
    fig, ax = plt.subplots()
    ax.plot(dates, ss_prices, 'r-', label='SH')
    ax.plot(dates, spy_prices, 'b-', label='SPY')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=8, borderaxespad=0.)
    plt.show()


if __name__ == '__main__':
    credits_df = NYSECreditDAO().get_all_margin_debt()
    #date_str_list = map(lambda x: x.date_str, credits)
    spy_df = YahooEquityDAO().get_equity_monthly_by_symbol('^GSPC', ['adjcloseprice'])
    ss_df = YahooEquityDAO().get_equity_monthly_by_symbol('000001.ss', ['adjcloseprice'])
    plot_lines(credits_df, spy_df, ss_df)
