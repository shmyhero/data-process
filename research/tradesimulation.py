import math
from dataaccess.basicdao import BasicDao


class TradeAccount(object):

    def __init__(self, init_cash=1000000, buy_tax=0.001, sell_tax=0.001):
        self.holds = {}
        self.daily_data_cache = {}
        self.cash = init_cash
        self.buy_tax = buy_tax
        self.sell_tax = sell_tax

    def get_price_by_date_str(self, code, date_str):
        if self.daily_data_cache.has_key(code):
            df = self.daily_data_cache[code]
        else:
            df = BasicDao.load_daily_data(code)
            self.daily_data_cache[code] = df
        record = df[df.TIME >= date_str].iloc[0]
        return record['CLOSE']

    def get_total_asset(self, date_str):
        total = self.cash
        for code, quantity in self.holds.items():
            total += quantity * self.get_price_by_date_str(code, date_str)
        return total

    def buy(self, date_str, code, buy_cash=None):
        price = self.get_price_by_date_str(code, date_str)
        if buy_cash is None:
            buy_cash = self.cash
        if self.cash < buy_cash:
            raise Exception('Not enough cash, left cash:{}, desired cash:{}'.format(self.cash, buy_cash))
        quantity = math.floor(buy_cash / (price * (1 + self.buy_tax)))
        spend_cash = price * quantity * (1 + self.buy_tax)
        if self.holds.has_key(code):
            self.holds[code] += quantity
        else:
            self.holds[code] = quantity
        self.cash -= spend_cash

    def sell(self, date_str, code, quantity=None):
        if quantity is None:
            quantity = self.holds[code]
        elif quantity > self.holds[code]:
            raise Exception('Not enough asset for to sell')
        else:
            pass
        price = self.get_price_by_date_str(code, date_str)
        received_cash = price * quantity * (1 - self.sell_tax)
        self.holds[code] -= quantity
        self.cash += received_cash


if __name__ == '__main__':
    from pathmgr import PathMgr
    import pandas as pd
    df = pd.read_csv(PathMgr.get_historical_etf_path('SPY'))
    trade = TradeAccount()
