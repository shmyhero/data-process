import time
import datetime
from utils.httphelper import HttpHelper


class WebScraper(object):

    def __init__(self):
        pass

    @staticmethod
    def http_get_with_retry(url, times = 3):
        try:
            return HttpHelper.http_get(url)
        except Exception:
            if times > 0:
                time.sleep(1)
                return WebScraper.http_get_with_retry(url, times-1)
            else:
                raise Exception('Failed to get data from %s'%url, )

    @staticmethod
    def get_expiration_dates(symbol):
        url_template = 'https://core-api.barchart.com/v1/options/chain?fields=&symbol={}&groupBy=&gt(volatility,0)=&meta=&raw=&expirationDate='
        url = url_template.format(symbol)
        return WebScraper.http_get_with_retry(url)

    @staticmethod
    def get_equity_data(symbol):
        #url_template = 'https://core-api.barchart.com/v1/quotes/get?symbols={}&fields=lastPrice&meta=&raw=1'
        #url_template = 'https://core-api.barchart.com/v1/quotes/get?symbols={}&fields=symbol,tradeTime,lastPrice'
        url_template = 'https://core-api.barchart.com/v1/quotes/get?symbols={}&fields=symbol,tradeTime,openPrice,highPrice,lowPrice,lastPrice,priceChange,volume'
        #, lastPrice, priceChange, openPrice, highPrice, lowPrice, previousPrice, volume, openInterest, tradeTime, symbolCode, symbolType, hasOptions
        url = url_template.format(symbol)
        return WebScraper.http_get_with_retry(url)

    @staticmethod
    def get_option_data(symbol, expiration_date):
        """
        get option fields value includes expirationDate,optionType,strikePrice,askPrice,bidPrice,lastPrice,priceChange,volatility,theoretical,delta,gamma,rho,theta,vega,openInterest,volume
        :param symbol:
        :param expiration_date: the expiration-date format is yyyy-MM-dd
        :return:
        """
        if datetime.datetime.now().weekday() > 1 and datetime.datetime.now().weekday() < 5:
            url_template = 'https://core-api.barchart.com/v1/options/chain?fields=symbol,expirationDate,date,daysToExpiration,optionType,strikePrice,askPrice,bidDate,bidPrice,openPrice,highPrice,lowPrice,lastPrice,priceChange,volatility,theoretical,delta,gamma,rho,theta,vega,openInterest,volume&symbol={}&groupBy=&gt(volatility,0)=&meta=&raw=&expirationDate={}'
        else: #bidDate can not get on weekend...
            url_template = 'https://core-api.barchart.com/v1/options/chain?fields=symbol,expirationDate,date,daysToExpiration,optionType,strikePrice,askPrice,bidPrice,openPrice,highPrice,lowPrice,lastPrice,priceChange,volatility,theoretical,delta,gamma,rho,theta,vega,openInterest,volume&symbol={}&groupBy=&gt(volatility,0)=&meta=&raw=&expirationDate={}'
        url = url_template.format(symbol, expiration_date)
        return WebScraper.http_get_with_retry(url)

    @staticmethod
    def get_vix_data():
        url = 'https://core-api.barchart.com/v1/quotes/get?fields=symbol,lastPrice,priceChange,openPrice,highPrice,lowPrice,previousPrice,volume,tradeTime,dailyLastPrice,dailyPriceChange,dailyOpenPrice,dailyHighPrice,dailyLowPrice,dailyPreviousPrice,dailyVolume,dailyDate1dAgo&list=futures.contractInRoot&root=VI&meta=&hasOptions=true&raw=&page=1'
        return WebScraper.http_get_with_retry(url)




if __name__ == '__main__':
    #print WebScraper.get_expiration_dates('SPY')
    #print WebScraper.get_equity_data('SPY')
    #print WebScraper.get_option_data('SPY', '2017-07-21')
    print WebScraper.get_vix_data()
    #import datetime
    #print type(datetime.date.today())


