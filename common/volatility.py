import math
import numpy as np
import vollib.black_scholes
import vollib.black_scholes.implied_volatility


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



if __name__ == "__main__":
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

