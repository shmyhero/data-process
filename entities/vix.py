import json
import datetime
from baseentity import BaseEntity


class VIX(BaseEntity):

    VIX_MONTH_NAMES = 'FGHJKMNQUVXZ'

    #NAME_RULES =
    @staticmethod
    def date_to_symbol(date_str):
        #date_str = date.strftime('%Y-%m-%d')
        ymd = date_str.split('-')
        month = int(float (ymd[1]))
        return 'VI{}{}'.format(VIX.VIX_MONTH_NAMES[month-1], ymd[0][2:])

    #:TODO change it to from_date
    @staticmethod
    def get_next_symbols(from_date_str, count=3):
        ymd = from_date_str.split('-')
        month = int(float(ymd[1]))
        year = int(float(ymd[0][2:]))
        for i in range(count):
            m = month + i
            y = year
            if m > 12:
                delta = m/12
                m = m - delta*12
                y = y + delta
            yield 'VI%s%02d'%(VIX.VIX_MONTH_NAMES[m-1], y)

    #TODO:change it to from date.
    @staticmethod
    def get_following_symbols(from_date_str, count = 2):
        next_symbols = list(VIX.get_next_symbols(from_date_str, count+1))
        date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d')
        if date.day >= 21 or (date.day > 14 and date.weekday() > 1):
            return next_symbols[1:count+1]
        else:
            return next_symbols[0:count]

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
    print VIX.date_to_symbol('2017-09-05')
    print list(VIX.get_following_symbols('2017-09-19'))
    print list(VIX.get_following_symbols('2017-09-27'))
    print list(VIX.get_following_symbols('2017-08-16'))