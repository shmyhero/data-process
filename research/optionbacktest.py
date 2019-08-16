import datetime
from utils.listhelper import hash_to_list
from common.tradetime import TradeTime
from research.tradesimulation import DataProvider


class OptionQuantity(object):

    def __init__(self, option_symbol, quantity, long_short, start_date):
        self.option_symbol = option_symbol
        self.quantity = quantity
        self.long_short = long_short
        self.start_date = start_date

    def get_expiration_date(self):
        date_ymd = self.option_symbol[-15:-9]
        return datetime.datetime.strptime(date_ymd, '%y%m%d').date()

    def get_date_values(self):
        expiration_date = self.get_expiration_date()
        latest_date = min(TradeTime.get_latest_trade_date(), expiration_date)
        days = (latest_date - self.start_date).days
        for i in range(days+1):
            date = self.start_date + datetime.timedelta(days=i)
            if TradeTime.is_trade_day(date):
                value = DataProvider.get_price_by_date(self.option_symbol, date)
                #print 'date=%s,value=%s'%(date,value)
                if value is not None:
                    if self.long_short.lower() == 'short':
                        value = -value
                    yield [date, self.quantity*value]


class OptionBackTest(object):

    def __init__(self, option_quantity_list, start_date):
        self.option_quantity_list = option_quantity_list
        self.start_date = start_date
        self.option_quantity_objects = list(self._init_option_quantities())

    def _init_option_quantities(self):
        for [option_symbol, quantity, long_short] in self.option_quantity_list:
            yield OptionQuantity(option_symbol, quantity, long_short, self.start_date)

    def get_values(self):
        date_values_list = map(lambda x: list(x.get_date_values()), self.option_quantity_objects)
        sum_dic = {}
        for date_values in date_values_list:
            for date_value in date_values:
                [date, value] = date_value
                if sum_dic.get(date) is None:
                    sum_dic[date] = value
                else:
                    sum_dic[date] += value
        values = hash_to_list(sum_dic, True)
        continues_values = []
        for i, value in enumerate(values):
            if value[1] != 0:
                continues_values = values[i:]
                break
        benchmark = continues_values[0][1]
        if benchmark > 0 :
            return map(lambda x: [x[0], x[1]/benchmark], continues_values)
        else:
            return map(lambda x: [x[0], (2*benchmark-x[1])/benchmark], continues_values)


if __name__ == '__main__':
    for date_value in OptionBackTest([['SPY171020C00247000', 1, 'long']], datetime.date(2017, 8, 20)).get_values():
        print date_value
