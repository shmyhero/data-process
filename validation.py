import numpy as np
from dataaccess.data import Data

class Validator(object):

    def __init__(self):
        pass

    @staticmethod
    def validate_caa_data():
        data = Data()
        caa_stocks = ['LMT', 'MO', 'SPY', 'DIA', 'EFA', 'EEM', 'HYG', 'TLH', 'BIL']
        prices = data.history(caa_stocks, 'price', 260, '1d').dropna()
        N = len(caa_stocks)
        R = np.log(prices).diff().dropna()
        covar = R.cov().values
        R1 = (prices.iloc[-1] - prices.iloc[-21 * 1]) / prices.iloc[-21 * 1]  # recent 1 month return
        R3 = (prices.iloc[-1] - prices.iloc[-21 * 3]) / prices.iloc[-21 * 3]  # recent 3 month return
        R6 = (prices.iloc[-1] - prices.iloc[-21 * 6]) / prices.iloc[-21 * 6]  # recent 6 month return
        R12 = (prices.iloc[-1] - prices.iloc[-252]) / prices.iloc[-252]  # 1 year return
        R_mom = (R1 + R3 + R6 + R12) / 22