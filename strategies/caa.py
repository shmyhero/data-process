from algorithms.cla import CLA
from dataaccess.yahooequitydao import YahooEquityDAO
from research.tradesimulation import TradeAccount, TradeNode, TradeSimulation


class CAA(object):

    def __init__(self):
        self.symbols = ['SPY', 'QQQ', 'IEF']
        self.lower_bounds = [[0.00],[0.00],[0.00]]
        self.upper_bounds = [[0.25],[0.25],[1.00]]

    def get_prices(self, from_date_str):
        pass


#TODO: calculate covar& mean...
#covar = None
#mean = None
#cla = CLA(mean, covar, lower_bounds, upper_bounds)

#mu,sigma,weights=cla.efFrontier(1000)