import math
import numpy as np
import vollib.black_scholes
import vollib.black_scholes.implied_volatility
import vollib.black_scholes_merton
import vollib.black_scholes_merton.implied_volatility


class Volatility(object):

    @staticmethod
    def get_history_volatility(price_list):
        X = []
        for i in range(len(price_list)-2):
            X.append(math.log(price_list[i+1]/price_list[i]))
        return np.std(X)

    @staticmethod
    def get_year_history_volatility(price_list):
        return math.sqrt(252) * Volatility.get_history_volatility(price_list)

    @staticmethod
    def get_black_scholes_option_price(underlying_price, strike_price, days_to_experiation, risk_free_interest_rate, sigma, flag='c'):
        price = vollib.black_scholes.black_scholes(flag, underlying_price, strike_price, days_to_experiation, risk_free_interest_rate, sigma)
        return price


def spy_option():
    from dataaccess.yahooequitydao import YahooEquityDAO
    records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str= '2016-08-15')
    price_list = map(lambda x: x[1], records)
    underlying_price = price_list[-1]
    print 'underlying_price=%s'%underlying_price
    strike_price = 245
    interest_rate = 0.0167
    left_days = 27
    sigma = Volatility.get_history_volatility(price_list)
    print 'sigma=%s'%sigma
    #sigma = 0.0051
    bs_price = Volatility.get_black_scholes_option_price(underlying_price, strike_price, left_days/365.0, interest_rate, sigma, 'c')
    print 'bs_price=%s'%bs_price
    current_price = 3.67
    iv = vollib.black_scholes.implied_volatility.implied_volatility(current_price, underlying_price, strike_price, left_days/365.0, interest_rate, 'c')
    print iv

"""
def spy_historical_volatility():
    from dataaccess.equitydao import EquityDAO
    df = EquityDAO().select_by_symbols(['SPY'])
    price_list  = df['lastPrice']
    print df
    print Volatility.get_history_volatility(price_list)


def etf50_vol():
    price_list = [2.682, 2.724, 2.728, 2.689, 2.671, 2.679, 2.682, 2.644, 2.655]
    print Volatility.get_history_volatility(price_list)
    sigma = Volatility.get_year_history_volatility(price_list)
    print sigma
    sigma = 0.1358
    bs_price = Volatility.get_black_scholes_option_price(2.655, 2.7, 48/365.0, 0.032, sigma, 'p')
    print bs_price
    price = 0.071
    iv = vollib.black_scholes.implied_volatility.implied_volatility(price, 2.655, 2.7, 48/365.0, 0.032, 'p')
    print iv
"""

if __name__ == '__main__':
    spy_option()

