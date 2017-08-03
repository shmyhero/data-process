import json
from baseentity import BaseEntity


class Equity(BaseEntity):

    def __init__(self, symbol = None, tradeTime = None, openPrice = None, highPrice = None, lowPrice = None,
                 lastPrice = None, priceChange = None, volume = None):
        BaseEntity.__init__(self)
        self.symbol = symbol
        self.tradeTime = tradeTime
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.lastPrice = lastPrice
        self.priceChange = priceChange
        self.volume = volume

    @staticmethod
    def loads(dic):
        equity = Equity()
        for k, v in dic.items():
            setattr(equity, k, BaseEntity.fix_na(v))
        BaseEntity.parse_for_entity(BaseEntity.parse_float, equity, ['openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'priceChange', 'volume'])
        BaseEntity.parse_for_entity(BaseEntity.parse_date, equity, ['tradeTime'])
        return equity


