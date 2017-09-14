import datetime
from common.optionrules import OptionRules
from dataaccess.optiondao import OptionDAO
from dataaccess.equitydao import EquityDAO
from research.tradesimulation import TradeNode, TradeSimulation, Portfolio

"""classical option strategies"""

"""TODO: refactor it to a generic option combination... then consider include equity..."""


class SingleOption(object):

    def __init__(self, option_symbol, start_date, end_date=None, percentage = 1):
        self.option_symbol = option_symbol
        self.start_date = start_date
        if end_date is None:
            self.end_date = self.get_expiration_date()
        self.percentage = percentage

    def get_expiration_date(self):
        ymd = self.option_symbol[-15:-9]
        return datetime.datetime.strptime(ymd, '%y%m%d')

    def simulation(self):
        trade_nodes = [TradeNode(self.option_symbol, self.start_date, 'buy', percentage=self.percentage)]
        return TradeSimulation.simulate(trade_nodes, self.start_date, self.end_date)


class LongOption(SingleOption):

    def __init__(self, option_symbol, start_date, end_date=None, percentage = 1):
        SingleOption.__init__(self, option_symbol, start_date, end_date=None, percentage = 1)


class ShortOption(SingleOption):

    def __init__(self, option_symbol, start_date, end_date=None, percentage = 1):
        SingleOption.__init__(self, option_symbol, start_date, end_date=None, percentage = 1)
        self.percentege = -percentage


class Combination(object):

    def __init__(self, symbol, start_date, delta=0, days_to_expiration=20, percentages=[0.5, 0.5]):
        """
        hold the short combination till there are expired.
        :param symbol:
        :param start_date:
        :param delta:
        :param days_to_expiration: at least days to expiration.
        :param percentages: the percentages of cash for each options
        """
        self.symbol = symbol
        self.start_date = start_date
        self.delta = delta
        self.days_to_expiration = days_to_expiration
        self.init_option_symbols()
        self.percentages = percentages
        self.ratio = 1

    def find_expiration_date(self):
        dates = OptionDAO().get_all_unexpired_dates(self.symbol, self.start_date.strftime('%Y-%m-%d'))
        monthly_option_dates = OptionRules.find_monthly_option_dates(dates)
        for date in monthly_option_dates:
            dt = datetime.datetime.combine(date, datetime.time.min) - self.start_date
            if dt.days >= self.days_to_expiration:
                return date

    def init_option_symbols(self):
        expiration_date = self.find_expiration_date()
        start_date_price = EquityDAO().get_equity_price_by_date(self.symbol, self.start_date)
        days_to_current_date = (datetime.datetime.today() - self.start_date).days
        self.call_symbol = OptionDAO().find_symbol(self.symbol, expiration_date, start_date_price * (1+self.delta),\
                                              current_date=self.start_date, days_to_current_date=days_to_current_date, option_type='Call')
        self.put_symbol = OptionDAO().find_symbol(self.symbol, expiration_date, start_date_price * (1 - self.delta), \
                                              current_date=self.start_date, days_to_current_date=days_to_current_date, option_type='Put')



    def simulation(self):
        print self.call_symbol, self.put_symbol
        relative_percentages = list(TradeSimulation.get_relative_percentages(self.percentages))
        trade_nodes = [TradeNode(self.call_symbol, self.start_date, 'buy', percentage=relative_percentages[0]), \
                      TradeNode(self.put_symbol, self.start_date, 'buy', percentage=relative_percentages[1])]
        return TradeSimulation.simulate(trade_nodes, self.start_date)


class LongCombination(Combination):

    def __init__(self, symbol, start_date, delta=0, days_to_expiration=20, percentage = 1, ratio = 1):
        Combination.__init__(self, symbol, start_date, delta=delta, days_to_expiration=days_to_expiration, percentages=[0.5, 0.5])


class ShortCombination(Combination):

    def __init__(self, symbol, start_date, delta=0, days_to_expiration=20, percentage = -0.2, ratio=1):
        Combination.__init__(self, symbol, start_date, delta=delta, days_to_expiration=days_to_expiration, percentages=[0.1, 0.1])



if __name__ == '__main__':
    #returns = LongOption('SPY170915C00245000', datetime.datetime(2017, 8, 15)).simulation()
    #for [date, return_value] in returns:
    #    print date, return_value
    #print '-' * 80
    #returns = ShortOption('SPY170915C00245000', datetime.datetime(2017, 8, 15)).simulation()
    #for [date, return_value] in returns:
    #   print date, return_value
    #returns = ShortCombination('VXX', datetime.datetime(2017, 9, 1), delta=0).simulation()
    returns = LongCombination('VXX', datetime.datetime(2017, 9, 1), delta=0, percentage=[0.65, 0.35]).simulation()
    for [date, return_value] in returns:
        print date, return_value