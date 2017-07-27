import json
from baseentity import BaseEntity


class VIX(BaseEntity):

    #NAME_RULES = 'FGHJKMNQUVXZ'

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



