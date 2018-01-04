import datetime
import pandas as pd
import matplotlib.pyplot as plt
from dataaccess.yahooequitydao import YahooEquityDAO
from research.tradesimulation import TradeNode, TradeSimulation


class RollYield(object):

    def __init__(self):
        self.vix_records = YahooEquityDAO().get_all_equity_price_by_symbol('^VIX', from_date_str='2010-12-17')
        self.vxv_records = YahooEquityDAO().get_all_equity_price_by_symbol('^VXV', from_date_str='2010-12-17')
        self.dates = map(lambda x: x[0], self.vix_records)[7:]
        vix_values = map(lambda x: x[1], self.vix_records)
        self.vix_ma10 = pd.Series(vix_values).rolling(window=7).mean().tolist()[7:]
        vxv_values = map(lambda x: x[1], self.vxv_records)
        self.vxv_ma10 = pd.Series(vxv_values).rolling(window=7).mean().tolist()[7:]

    def run(self):
        trade_nodes = []
        previous_condition = False
        for i in range(len(self.dates)):
            #date = datetime.datetime.fromordinal(self.dates[i].toordinal())
            date = self.dates[i]
            if self.vxv_ma10[i] > self.vix_ma10[i]:
                if previous_condition is False:
                    #trade_nodes.append(TradeNode('VXX', date, 'sell'))
                    trade_nodes.append(TradeNode('XIV', date, 'buy'))
                    previous_condition = True
            else:
                if previous_condition is True:
                    trade_nodes.append(TradeNode('XIV', date, 'sell'))
                    #trade_nodes.append(TradeNode('VXX', date, 'buy'))
                    previous_condition = False
        returns = list(TradeSimulation.simulate(trade_nodes, self.dates[0]))
        #for [date, return_value] in returns:
        #    print date, return_value
        for trade_node in trade_nodes:
            print trade_node
        self.plot(returns)

    def plot(self, returns):
        fig, ax = plt.subplots()
        dates = map(lambda x: x[0], returns)
        values = map(lambda x: x[1], returns)
        ax.plot(dates, values)
        lines, labels = ax.get_legend_handles_labels()
        ax.legend(lines[:2], labels[:2])
        plt.show()

if __name__ == '__main__':
    RollYield().run()




