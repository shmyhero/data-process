import json
from baseentity import BaseEntity


class Option(BaseEntity):

    def __init__(self, underlingSymbol = None, tradeTime = None, symbol = None, expirationDate = None, daysToExpiration = None, date = None, optionType = None, strikePrice = None, askPrice = None, bidDate = None, bidPrice = None,
                 openPrice = None, highPrice = None, lowPrice = None, lastPrice = None, priceChange = None, volatility = None, theoretical = None, delta = None,
                 gamma = None, rho = None, theta = None, vega = None, openInterest = None, volume = None):
        BaseEntity.__init__(self)
        self.underlingSymbol = underlingSymbol
        self.tradeTime = tradeTime
        self.symbol = symbol
        self.expirationDate = expirationDate
        self.date = date
        self.daysToExpiration = daysToExpiration
        self.optionType = optionType
        self.strikePrice = strikePrice
        self.askPrice = askPrice
        self.bidDate = bidDate
        self.bidPrice = bidPrice
        self.openPrice = openPrice
        self.highPrice = highPrice
        self.lowPrice = lowPrice
        self.lastPrice = lastPrice
        self.priceChange = priceChange
        self.volatility = volatility
        self.theoretical = theoretical
        self.delta = delta
        self.gamma = gamma
        self.rho = rho
        self.theta = theta
        self.vega = vega
        self.openInterest = openInterest
        self.volume = volume

    @staticmethod
    def loads(dic):
        option = Option()
        for k, v in dic.items():
            setattr(option, k, BaseEntity.fix_na(v))
        BaseEntity.parse_for_entity(BaseEntity.parse_float, option, ['strikePrice', 'askPrice', 'bidPrice', 'openPrice', 'highPrice', 'lowPrice', 'lastPrice', 'priceChange', 'theoretical', 'delta', 'gamma', 'rho', 'theta', 'vega', 'openInterest', 'volume'])
        BaseEntity.parse_for_entity(BaseEntity.parse_date, option, ['tradeTime','expirationDate', 'date', 'bidDate'])
        option.volatility = BaseEntity.parse_float(option.volatility.replace('%', ''))
        return option



