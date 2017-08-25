import datetime
import numpy as np
import pandas as pd
from algorithms.cla import CLA
from dataaccess.yahooequitydao import YahooEquityDAO
from research.tradesimulation import TradeAccount, TradeNode, TradeSimulation


class CAA(object):

    def __init__(self):
        self.symbols = ['SPY', 'QQQ','EFA', 'EEM', 'EWJ', 'HYG', 'IEF', 'BIL']
        self.lower_bounds = [[0.00],[0.00],[0.00],[0.00],[0.00],[0.00],[0.00],[0.00]]
        self.upper_bounds = [[0.25],[0.25],[0.25],[0.25],[0.25],[0.25],[1.00],[1.00]]
        self.historical_prices = list(self.get_historical_prices())

    def get_historical_prices(self):
        yahooEquityDAO = YahooEquityDAO()
        for symbol in self.symbols:
            rows = yahooEquityDAO.get_all_equity_price_by_symbol(symbol)
            yield map(lambda x: x[1], rows)

    def get_prices_lists(self, days_ago):
        return map(lambda x: x[-days_ago-252:-days_ago], self.historical_prices)

    def getWeights(cla, tv):
        mu, sigma, weights = cla.efFrontier(1000)  # get effective fronter
        tv = tv / pow(252, 0.5)  # set target volatility, transfer to annual
        diff = 1000.0
        index = 0
        for i, value in enumerate(sigma):
            diff_now = abs(value - tv)
            if diff_now < diff:
                diff = diff_now
                index = i
        return weights[index]

    def get_covar(self, days_ago):
        prices_lists = self.get_prices_lists(days_ago)
        #print prices_lists
        #print np.diff(np.log(prices_lists))
        return np.cov(np.diff(np.log(prices_lists)))
        return None

    def get_mean_by_prices_list(self, days_ago):
        result = []
        for prices_list in self.get_prices_lists(days_ago):
            r12 = prices_list[-1]/prices_list[0] - 1
            r1 = prices_list[-1]/prices_list[-21] - 1
            r3 = prices_list[-1]/prices_list[-21 * 3] - 1
            r6 = prices_list[-1]/prices_list[-21 * 6] - 1
            r_mon = (r12 + r1 + r3 + r6)/22
            result.append([r_mon])
        return np.array(result)

    def rebalance(self, days_ago, tv):
        """
        :param days_ago:
        :param tv: target annual volatility
        :return:
        """
        mean = self.get_mean_by_prices_list(days_ago)
        covar = self.get_covar(days_ago)
        #print mean
        #print covar
        cla = CLA(mean, covar, self.lower_bounds, self.upper_bounds)
        cla.solve()
        weights = pd.Series(self.getWeights(cla, tv).flatten(), index=self.symbols)
        return weights


#cla = CLA(mean, covar, lower_bounds, upper_bounds)

#mu,sigma,weights=cla.efFrontier(1000)

if __name__ == '__main__':
    #print CAA().get_covar(8)
    #print CAA().get_mean_by_prices_list(8)
    print CAA().rebalance(8, 0.8)