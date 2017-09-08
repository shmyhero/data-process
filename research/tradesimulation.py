import math
import datetime
from dataaccess.yahooequitydao import YahooEquityDAO


class TradeNode(object):

    def __init__(self, symbol, date, action, percentage = 1):
        self.symbol = symbol
        self.date = date
        self.action = action
        self.percentage = percentage


class Portfolio(object):

    def __init__(self, init_cash=1000000, buy_tax=0.001, sell_tax=0.001, daily_data_cache = {}):
        self.position = {}
        self.daily_data_cache = daily_data_cache
        self.init_cash = init_cash
        self.cash = init_cash
        self.buy_tax = buy_tax
        self.sell_tax = sell_tax
        self.yahoo_equity_dao = YahooEquityDAO()

    def get_price_by_date_str(self, symbol, date_str):
        key = symbol + date_str
        if not self.daily_data_cache.has_key(key):
            price = self.yahoo_equity_dao.get_equity_price_by_date(symbol, date_str)
            self.daily_data_cache[key] = price
        return self.daily_data_cache[key]

    def get_portfolio_value(self, date_str):
        total = self.cash
        for symbol, quantity in self.position.items():
            total += quantity * self.get_price_by_date_str(symbol, date_str)
        return total

    def get_returns(self, date_str):
        return self.get_portfolio_value(date_str) / self.init_cash

    def buy(self, date_str, symbol, buy_cash=None):
        price = self.get_price_by_date_str(symbol, date_str)
        if buy_cash is None:
            buy_cash = self.cash
        if self.cash < buy_cash:
            raise Exception('Not enough cash, left cash:{}, desired cash:{}'.format(self.cash, buy_cash))
        quantity = math.floor(buy_cash / (price * (1 + self.buy_tax)))
        spend_cash = price * quantity * (1 + self.buy_tax)
        if self.position.has_key(symbol):
            self.position[symbol] += quantity
        else:
            self.position[symbol] = quantity
        self.cash -= spend_cash

    def sell(self, date_str, symbol, quantity=None):
        if quantity is None:
            quantity = self.position[symbol]
        elif quantity > self.position[symbol]:
            raise Exception('Not enough asset for to sell')
        else:
            pass
        price = self.get_price_by_date_str(symbol, date_str)
        received_cash = price * quantity * (1 - self.sell_tax)
        self.position[symbol] -= quantity
        self.cash += received_cash

    def action(self, trade_node):
        if trade_node.action == 'buy':
            self.buy(trade_node.date.strftime('%Y-%m-%d'), trade_node.symbol, self.cash * trade_node.percentage)
        elif trade_node.action == 'sell':
            self.sell(trade_node.date.strftime('%Y-%m-%d'), trade_node.symbol, self.position[trade_node.symbol] * trade_node.percentage)
        else:
            raise AssertionError('the trade date should be in dates ranges.')


class TradeSimulation(object):

    daily_data_cache = {}

    @staticmethod
    def date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + datetime.timedelta(n)

    @staticmethod
    def simulate(trade_nodes, start_date, end_date = datetime.datetime.today()):
        portfolio = Portfolio(daily_data_cache = TradeSimulation.daily_data_cache)
        dates = list(TradeSimulation.date_range(start_date, end_date))
        print trade_nodes
        print dates
        i = 0
        j = 0
        while i < len(dates) or j < len(trade_nodes):
            if j < len(trade_nodes) and dates[i] > trade_nodes[j].date:
                raise AssertionError('the trade date should be in dates ranges.')
            elif j < len(trade_nodes) and dates[i] == trade_nodes[j].date:
                portfolio.action(trade_nodes[j])
                j += 1
            else:
                date_str = dates[i].strftime('%Y-%m-%d')
                print (date_str, portfolio.get_returns(date_str))
                i += 1


if __name__ == '__main__':
    #trade = TradeAccount()
    #trade.buy('2017-01-01', 'SPY')
    #print trade.get_net_value('2017-07-01')
    trade_nodes = [TradeNode('QQQ', datetime.datetime.strptime('2017-01-01', '%Y-%m-%d'), 'buy'),
                   TradeNode('QQQ', datetime.datetime.strptime('2017-02-23', '%Y-%m-%d'), 'sell'),
                   TradeNode('SPY', datetime.datetime.strptime('2017-02-23', '%Y-%m-%d'), 'buy'),
                   TradeNode('SPY', datetime.datetime.strptime('2017-03-07', '%Y-%m-%d'), 'sell'),
                   TradeNode('QQQ', datetime.datetime.strptime('2017-03-07', '%Y-%m-%d'), 'buy'),
                   TradeNode('QQQ', datetime.datetime.strptime('2017-06-09', '%Y-%m-%d'), 'sell'),
                   TradeNode('SPY', datetime.datetime.strptime('2017-06-09', '%Y-%m-%d'), 'buy'),
                   TradeNode('SPY', datetime.datetime.strptime('2017-06-13', '%Y-%m-%d'), 'sell'),
                   TradeNode('QQQ', datetime.datetime.strptime('2017-06-13', '%Y-%m-%d'), 'buy'),
                   ]
    TradeSimulation.simulate(trade_nodes, datetime.datetime.strptime('2017-01-01', '%Y-%m-%d'))
