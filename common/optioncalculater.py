import math
import numpy as np
import vollib.black_scholes
import vollib.black_scholes.implied_volatility
import vollib.black_scholes_merton
import vollib.black_scholes_merton.implied_volatility
import vollib.black_scholes.greeks.numerical


class OptionCalculater(object):

    @staticmethod
    def get_history_volatility(price_list):
        X = []
        for i in range(len(price_list)-2):
            X.append(math.log(price_list[i+1]/price_list[i]))
            #X.append((price_list[i + 1] - price_list[i])/price_list[i])
        #print X
        return np.std(X)

    @staticmethod
    def get_history_volatility2(price_list):
        dailyVolatility = np.std(np.diff(np.log(price_list)))
        return dailyVolatility

    @staticmethod
    def get_year_history_volatility(price_list):
        return math.sqrt(252) * OptionCalculater.get_history_volatility2(price_list)

    @staticmethod
    def get_year_history_volatility_list(date_price_records, circle = 30):
        length = len(date_price_records)
        results = []
        for i in range(length-circle):
            price_list = map(lambda x: x[1], date_price_records[i:i+circle])
            vol = OptionCalculater.get_year_history_volatility(price_list)
            results.append([date_price_records[i+circle][0], vol])
        return results

    @staticmethod
    def get_black_scholes_option_price(underlying_price, strike_price, days_to_experiation, risk_free_interest_rate, sigma, flag='c'):
        price = vollib.black_scholes.black_scholes(flag, underlying_price, strike_price, days_to_experiation, risk_free_interest_rate, sigma)
        return price

    @staticmethod
    def get_implied_volatility(current_price, underlying_price, strike_price, left_days, interest_rate, flag='c'):
        return vollib.black_scholes.implied_volatility.implied_volatility(current_price, underlying_price, strike_price,
                                                                   left_days / 365.0, interest_rate, flag)

    @staticmethod
    def get_delta(underlying_price, strike_price, left_days, risk_free_interest_rate, sigma, flag='c'):
        delta = vollib.black_scholes.greeks.numerical.delta(flag, underlying_price, strike_price, left_days/365.0, risk_free_interest_rate, sigma)
        return delta

    @staticmethod
    def get_gamma(underlying_price, strike_price, left_days, risk_free_interest_rate, sigma, flag='c'):
        gamma = vollib.black_scholes.greeks.numerical.gamma(flag, underlying_price, strike_price, left_days/365.0, risk_free_interest_rate, sigma)
        return gamma

    @staticmethod
    def get_gamma(underlying_price, strike_price, left_days, risk_free_interest_rate, sigma, flag='c'):
        gamma = vollib.black_scholes.greeks.numerical.gamma(flag, underlying_price, strike_price, left_days/365.0, risk_free_interest_rate, sigma)
        return gamma

    @staticmethod
    def get_vega(underlying_price, strike_price, left_days, risk_free_interest_rate, sigma, flag='c'):
        vega = vollib.black_scholes.greeks.numerical.vega(flag, underlying_price, strike_price, left_days/365.0, risk_free_interest_rate, sigma)
        return vega

    @staticmethod
    def get_theta(underlying_price, strike_price, left_days, risk_free_interest_rate, sigma, flag='c'):
        theta = vollib.black_scholes.greeks.numerical.theta(flag, underlying_price, strike_price, left_days/365.0, risk_free_interest_rate, sigma)
        return theta

    @staticmethod
    def get_rho(underlying_price, strike_price, left_days, risk_free_interest_rate, sigma, flag='c'):
        rho = vollib.black_scholes.greeks.numerical.rho(flag, underlying_price, strike_price, left_days/365.0, risk_free_interest_rate, sigma)
        return rho


def spy_option():
    from dataaccess.yahooequitydao import YahooEquityDAO
    records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str= '2017-07-21')
    price_list = map(lambda x: x[1], records)
    #from dataaccess.equitydao import EquityDAO
    #df = EquityDAO().select_by_symbols(['SPY'])
    #print df
    #price_list = df['lastPrice'].tolist()
    #print price_list
    underlying_price = price_list[-1]
    print 'underlying_price=%s'%underlying_price
    strike_price = 245
    interest_rate = 0.005
    left_days = 24
    sigma = OptionCalculater.get_year_history_volatility(price_list)
    print 'sigma=%s'%sigma
    bs_price = OptionCalculater.get_black_scholes_option_price(underlying_price, strike_price, left_days / 365.0, interest_rate, sigma, 'c')
    print 'bs_price=%s'%bs_price
    current_price = 1.53
    iv = OptionCalculater.get_implied_volatility(current_price, underlying_price, strike_price, left_days, interest_rate, 'c')
    print 'implied volatility:%s'%iv
    delta = OptionCalculater.get_delta(underlying_price, strike_price, left_days, interest_rate, sigma, 'c')
    print 'delta=%s' % delta
    gamma = OptionCalculater.get_gamma(underlying_price, strike_price, left_days, interest_rate, sigma, 'c')
    print 'gamma=%s' % gamma
    vega = OptionCalculater.get_vega(underlying_price, strike_price, left_days, interest_rate, sigma, 'c')
    print 'vega=%s' % vega
    theta = OptionCalculater.get_theta(underlying_price, strike_price, left_days, interest_rate, sigma, 'c')
    print 'theta=%s' % theta
    rho = OptionCalculater.get_rho(underlying_price, strike_price, left_days, interest_rate, sigma, 'c')
    print 'rho=%s' % rho

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


def _test_vol():
    import datetime
    from dataaccess.yahooequitydao import YahooEquityDAO
    from_date_str = (datetime.date.today() - datetime.timedelta(100)).strftime('%Y-%m-%d')
    equity_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str)
    results = OptionCalculater.get_year_history_volatility_list(equity_records)
    print results

if __name__ == '__main__':
    spy_option()
    #_test_vol()

