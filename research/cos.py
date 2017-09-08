from common.optionrules import OptionRules
from dataaccess.optiondao import OptionDAO
from dataaccess.equitydao import EquityDAO

"""classical option strategies"""

"""TODO: refactor it to a generic option combination... then consider include equity..."""
class ShortCombination(object):

    def __init__(self, symbol, start_date, delta=0.03, days_to_expiration=20):
        """
        hold the short combination till there are expired.
        :param symbol:
        :param start_date:
        :param delta:
        :param days_to_expiration: at least days to expiration.
        """
        self.symbol = symbol
        self.start_date = start_date
        self.delta = delta
        self.days_to_expiration = days_to_expiration
        self.init_option_symbols()

    def find_expiration_date(self):
        dates = OptionDAO().get_all_unexpired_dates(self.symbol, self.start_date.strftime('%Y-%m-%d'))
        monthly_option_dates = OptionRules.find_monthly_option_dates(dates)
        for date in monthly_option_dates:
            dt = date - self.days_to_expiration
            if dt.days >= 20:
                return date

    def init_option_symbols(self):
        expiration_date = self.find_expiration_date()
        start_date_price = EquityDAO().get_equity_price_by_date(self.symbol, self.start_date)
        self.call_symbol = OptionDAO().find_symbol(self.symbol, expiration_date, start_date_price * (1-self.delta),\
                                              current_date=self.start_date, days_to_current_date=1, option_type='Call')
        self.put_symbol = OptionDAO().find_symbol(self.symbol, expiration_date, start_date_price * (1 + self.delta), \
                                              current_date=self.start_date, days_to_current_date=1, option_type='Put')


    def get_returns(self):
        pass