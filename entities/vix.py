import json
import datetime
from common.tradetime import TradeTime
from baseentity import BaseEntity


class VIX(BaseEntity):

    VIX_MONTH_NAMES = 'FGHJKMNQUVXZ'

    #@staticmethod
    #def get_next_symbols(from_date, count=3):
    #    year = from_date.year
    #    month = from_date.month
    #    for i in range(count):
    #        m = month + i
    #        y = year
    #        if m > 12:
    #            delta = m/12
    #            m = m - delta*12
    #            y = y + delta
    #        yield 'VI%s%02d'%(VIX.VIX_MONTH_NAMES[m-1], y)

    #@staticmethod
    #def get_following_symbols(from_date, count = 2):
    #    next_symbols = list(VIX.get_next_symbols(from_date, count+1))
    #    if from_date.day >= 21 or (from_date.day > 17 and from_date.weekday() > 1):
    #        return next_symbols[1:count+1]
    #    else:
    #        return next_symbols[0:count]

    @staticmethod
    def get_following_expiration_date(current_date):
        month = current_date.month
        day = current_date.day
        weekday = datetime.date(current_date.year, month, 1).weekday()
        delta = 2 - weekday
        if delta <= 0:
            delta += 7
        expiration_day = 1 + 2 * 7 + delta
        year = current_date.year
        if day >= expiration_day:
            month += 1
            if month >= 12:
                month -= 12
                year += 1
        return datetime.date(year, month, expiration_day)


    @staticmethod
    def get_following_year_index(current_date):
        date = VIX.get_following_expiration_date(current_date)
        return date.year, date.month-1


    @staticmethod
    def get_year_index_list(from_date, to_date, fx=1):
        (from_year, from_index) = VIX.get_following_year_index(from_date)
        (to_year, to_index) = VIX.get_following_year_index(to_date)
        to_index += fx - 1
        count = (to_year-from_year) * 12 + to_index - from_index
        for i in range(count + 1):
            year = from_year
            index = from_index + i
            if index >= 12:
                delta_year = index / 12
                index = index - delta_year * 12
                year = year + delta_year
            yield (year, index)

    @staticmethod
    def get_symbol_by_year_index(year, index):
        return 'VI%s%02d'%(VIX.VIX_MONTH_NAMES[index], year%100)

    @staticmethod
    def get_f1_by_date(date):
        (year, index) = VIX.get_following_year_index(date)
        return VIX.get_symbol_by_year_index(year, index)

    @staticmethod
    def get_f2_by_date(date):
        (year, index) = VIX.get_following_year_index(date)
        return VIX.get_symbol_by_year_index(year, index+1)

    @staticmethod
    def get_vix_symbol_list(from_date, to_date = None, fx=1):
        to_date = to_date or TradeTime.get_latest_trade_date()
        for (year, index) in VIX.get_year_index_list(from_date, to_date, fx):
            yield VIX.get_symbol_by_year_index(year, index)

    def __init__(self, symbol = None, lastPrice = None, priceChange = None, openPrice = None, highPrice = None, lowPrice = None,
                 previousPrice = None, volume = None, tradeTime = None, dailyLastPrice = None, dailyPriceChange = None, dailyOpenPrice = None,
                 dailyHighPrice = None, dailyLowPrice = None, dailyPreviousPrice = None, dailyVolume = None, dailyDate1dAgo = None):
        BaseEntity.__init__(self)
        self.symbol = symbol
        self.lastPrice = lastPrice
        self.priceChange = priceChange
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.previousPrice = previousPrice
        self.volume = volume
        self.tradeTime = tradeTime
        self.dailyLastPrice = dailyLastPrice
        self.dailyPriceChange = dailyPriceChange
        self.dailyOpenPrice = dailyOpenPrice
        self.dailyHighPrice = dailyHighPrice
        self.dailyLowPrice = dailyLowPrice
        self.dailyPreviousPrice = dailyPreviousPrice
        self.dailyVolume = dailyVolume
        self.dailyDate1dAgo = dailyDate1dAgo

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def loads(dic):
        vix = VIX()
        for k, v in dic.items():
            setattr(vix, k, BaseEntity.fix_na(v))
        BaseEntity.parse_for_entity(BaseEntity.parse_float, vix,
                                    ['lastPrice', 'priceChange', 'openPrice', 'highPrice', 'lowPrice', 'previousPrice','volume','dailyLastPrice','dailyPriceChange','dailyOpenPrice','dailyHighPrice','dailyLowPrice','dailyPreviousPrice','dailyVolume'])
        BaseEntity.parse_for_entity(BaseEntity.parse_date, vix, ['dailyDate1dAgo'])
        return vix


if __name__ == '__main__':
    print VIX.get_f1_by_date(datetime.datetime(2017, 12, 25))
    print VIX.get_f1_by_date(datetime.datetime(2017, 9, 15))
    print VIX.get_f1_by_date(datetime.datetime(2017, 9, 19))
    print VIX.get_f2_by_date(datetime.datetime(2017, 9, 20))
    print VIX.get_following_expiration_date(datetime.datetime(2017, 12, 25))
    print list(VIX.get_vix_symbol_list(datetime.datetime(2017, 8, 10), datetime.datetime(2017, 9, 20), 2))