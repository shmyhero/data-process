import math
import datetime
from utils.cachehelper import CacheMan
from common.tradetime import TradeTime
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.optiondao import OptionDAO


class TradeNode(object):

    def __init__(self, symbol, date, action, percentage = 1):
        self.symbol = symbol
        self.date = date
        self.action = action
        self.percentage = percentage


class DataProvider(object):

    @staticmethod
    def _get_equity_price_list_as_dic(symbol):
        records = YahooEquityDAO().get_all_equity_price_by_symbol(symbol)
        result = {}
        for [d,v] in records:
            result[int(d.strftime('%Y%m%d'))] = v
        return result

    @staticmethod
    def _get_option_price_list_as_dic(option_symbol):
        records = OptionDAO().compatible_get_option_by_symbol(option_symbol)
        result = {}
        for record in records:
            d = int(record[0].strftime('%Y%m%d'))
            v = record[1]
            result[d] = v
        return result

    @staticmethod
    def get_equity_price_records(symbol):
        return CacheMan('yahoo_equity_price').get_with_cache(symbol, DataProvider._get_equity_price_list_as_dic)

    @staticmethod
    def get_option_price_records(option_symbol):
        return CacheMan('option_date_price').get_with_cache(option_symbol, DataProvider._get_option_price_list_as_dic)

    @staticmethod
    def find_price(date_price_dic, the_date, recusion_count = 10):
        date_key = int(the_date.strftime('%Y%m%d'))
        if date_price_dic.has_key(date_key):
            return date_price_dic[date_key]
        else:
            if recusion_count > 0:
                return DataProvider.find_price(date_price_dic, the_date - datetime.timedelta(days=1), recusion_count -1)
            else:
                return None

    @staticmethod
    def get_price_by_date(symbol, the_date):
        if len(symbol) < 15:  # it's equity
            records_dic = DataProvider.get_equity_price_records(symbol)
            return DataProvider.find_price(records_dic, the_date)
        else:
            records_dic = DataProvider.get_option_price_records(symbol)
            return DataProvider.find_price(records_dic, the_date)


class Portfolio(object):

    def __init__(self, init_cash=1000000, buy_tax=0.001, sell_tax=0.001):
        self.position = {}
        self.init_cash = init_cash
        self.cash = init_cash
        self.buy_tax = buy_tax
        self.sell_tax = sell_tax
        self.yahoo_equity_dao = YahooEquityDAO()
        self.option_dao = OptionDAO()

    def get_portfolio_value(self, date):
        total = self.cash
        for symbol, quantity in self.position.items():
            total += quantity * DataProvider.get_price_by_date(symbol, date)
        return total

    def get_returns(self, date):
        return self.get_portfolio_value(date) / self.init_cash

    def buy(self, date, symbol, buy_cash=None):
        price = DataProvider.get_price_by_date(symbol, date)
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

    def sell(self, date, symbol, quantity=None):
        if quantity is None:
            quantity = self.position[symbol]
        elif quantity > self.position[symbol]:
            raise Exception('Not enough asset for to sell')
        else:
            pass
        price = DataProvider.get_price_by_date(symbol, date)
        received_cash = price * quantity * (1 - self.sell_tax)
        self.position[symbol] -= quantity
        self.cash += received_cash

    def action(self, trade_node):
        if trade_node.action == 'buy':
            self.buy(trade_node.date, trade_node.symbol, self.cash * trade_node.percentage)
        elif trade_node.action == 'sell':
            if self.position.has_key(trade_node.symbol):
                self.sell(trade_node.date, trade_node.symbol, self.position[trade_node.symbol] * trade_node.percentage)
        else:
            raise AssertionError('the trade date should be in dates ranges.')


class TradeSimulation(object):

    @staticmethod
    def date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + datetime.timedelta(n)

    @staticmethod
    def get_relative_percentages(percentages):
        """
        #list(get_relative_percentages([0.1, 0.1, 0.1]))
        #=>[0.1, 0.11111111111111112, 0.125]
        :param percentages:
        :return:
        """
        total = 1
        for percentage in percentages:
            new_percentage = percentage/total
            total -= percentage
            yield new_percentage

    @staticmethod
    def simulate(trade_nodes, start_date, end_date = None):
        if end_date is None:
            end_date = TradeTime.get_latest_trade_date()
        portfolio = Portfolio()
        dates = list(TradeSimulation.date_range(start_date, end_date))
        #print trade_nodes
        #print dates
        i = 0
        j = 0
        while i < len(dates) or j < len(trade_nodes):
            if j < len(trade_nodes) and dates[i] > trade_nodes[j].date:
                raise AssertionError('the trade date should be in dates ranges.')
            elif j < len(trade_nodes) and dates[i] == trade_nodes[j].date:
                portfolio.action(trade_nodes[j])
                j += 1
            else:
                #date_str = dates[i].strftime('%Y-%m-%d')
                #print (date_str, portfolio.get_returns(dates[i]))
                yield [dates[i], portfolio.get_returns(dates[i])]
                i += 1


if __name__ == '__main__':
    trade = Portfolio()
    trade.buy(datetime.datetime(2017, 1, 1), 'QQQ')
    print trade.get_returns(datetime.datetime(2017, 9, 13))
    trade_nodes = [TradeNode('QQQ', datetime.date(2017, 1, 1), 'buy'),
                   TradeNode('QQQ', datetime.date(2017, 2, 23), 'sell'),
                   TradeNode('SPY', datetime.date(2017, 2, 23), 'buy'),
                   TradeNode('SPY', datetime.date(2017, 3, 7), 'sell'),
                   TradeNode('QQQ', datetime.date(2017, 3, 7), 'buy'),
                   TradeNode('QQQ', datetime.date(2017, 6, 9), 'sell'),
                   TradeNode('SPY', datetime.date(2017, 6, 9), 'buy'),
                   TradeNode('SPY', datetime.date(2017, 6, 13), 'sell'),
                   TradeNode('QQQ', datetime.date(2017, 6, 13), 'buy'),
                   ]
    returns = TradeSimulation.simulate(trade_nodes, datetime.date(2017, 1, 1))
    for [date, return_value] in returns:
        print date, return_value
