import datetime
import numpy as np
from algorithms.cla import CLA
from dataaccess.yahooequitydao import YahooEquityDAO
from research.tradesimulation import TradeAccount, TradeNode, TradeSimulation


class CAA(object):

    def __init__(self):
        self.symbols = ['SPY', 'QQQ', 'IEF']
        self.lower_bounds = [[0.00],[0.00],[0.00]]
        self.upper_bounds = [[0.25],[0.25],[1.00]]
        self.prices_lists = list(self.get_price_lists())

    def get_price_lists(self):
        yahooEquityDAO = YahooEquityDAO()
        from_date = datetime.datetime.today() - datetime.timedelta(days=252)
        from_date_str = from_date.strftime('%Y-%m-%d')
        for symbol in self.symbols:
            rows = yahooEquityDAO.get_all_equity_price_by_symbol(symbol, from_date_str)
            yield map(lambda x: x[1], rows)

    def get_covar(self):
        print self.prices_lists
        print np.diff(np.log(self.prices_lists))
        return np.cov(np.diff(np.log(self.prices_lists)))







#TODO: calculate covar& mean...
#covar = None
#mean = None
#cla = CLA(mean, covar, lower_bounds, upper_bounds)

#mu,sigma,weights=cla.efFrontier(1000)

if __name__ == '__main__':
    print CAA().get_covar()