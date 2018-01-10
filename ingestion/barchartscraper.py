import time
import datetime
import traceback
import json
from utils.logger import Logger
from utils.httphelper import HttpHelper


class BarchartScraper(object):

    def __init__(self):
        pass

    @staticmethod
    def http_get_with_retry(url, times = 3):
        try:
            return HttpHelper.http_get(url)
        except Exception:
            if times > 0:
                time.sleep(1)
                url = url.replace('bidDate,', '')  # sometime the bidDate field is unavailable..
                return BarchartScraper.http_get_with_retry(url, times - 1)
            else:
                raise Exception('Failed to get data from %s'%url, )

    @staticmethod
    def get_expiration_dates(symbol):
        url_template = 'https://core-api.barchart.com/v1/options/chain?fields=&symbol={}&groupBy=&gt(volatility,0)=&meta=&raw=&expirationDate='
        url = url_template.format(symbol)
        return BarchartScraper.http_get_with_retry(url)

    @staticmethod
    def get_equity_data(symbol):
        #url_template = 'https://core-api.barchart.com/v1/quotes/get?symbols={}&fields=lastPrice&meta=&raw=1'
        #url_template = 'https://core-api.barchart.com/v1/quotes/get?symbols={}&fields=symbol,tradeTime,lastPrice'
        url_template = 'https://core-api.barchart.com/v1/quotes/get?symbols={}&fields=symbol,tradeTime,openPrice,highPrice,lowPrice,lastPrice,priceChange,volume'
        #, lastPrice, priceChange, openPrice, highPrice, lowPrice, previousPrice, volume, openInterest, tradeTime, symbolCode, symbolType, hasOptions
        url = url_template.format(symbol)
        return BarchartScraper.http_get_with_retry(url)

    @staticmethod
    def get_option_data(symbol, expiration_date):
        """
        get option fields value includes expirationDate,optionType,strikePrice,askPrice,bidPrice,lastPrice,priceChange,volatility,theoretical,delta,gamma,rho,theta,vega,openInterest,volume
        :param symbol:
        :param expiration_date: the expiration-date format is yyyy-MM-dd
        :return:
        """
        #if datetime.datetime.now().weekday() > 1 and datetime.datetime.now().weekday() < 5:
        url_template = 'https://core-api.barchart.com/v1/options/chain?fields=symbol,expirationDate,date,daysToExpiration,optionType,strikePrice,askPrice,bidDate,bidPrice,openPrice,highPrice,lowPrice,lastPrice,priceChange,volatility,theoretical,delta,gamma,rho,theta,vega,openInterest,volume&symbol={}&groupBy=&gt(volatility,0)=&meta=&raw=&expirationDate={}'
        #else: #bidDate can not get on weekend...
        #url_template = 'https://core-api.barchart.com/v1/options/chain?fields=symbol,expirationDate,date,daysToExpiration,optionType,strikePrice,askPrice,bidPrice,openPrice,highPrice,lowPrice,lastPrice,priceChange,volatility,theoretical,delta,gamma,rho,theta,vega,openInterest,volume&symbol={}&groupBy=&gt(volatility,0)=&meta=&raw=&expirationDate={}'
        url = url_template.format(symbol, expiration_date)
        return BarchartScraper.http_get_with_retry(url)

    @staticmethod
    def get_vix_data():
        url = 'https://core-api.barchart.com/v1/quotes/get?fields=symbol,lastPrice,priceChange,openPrice,highPrice,lowPrice,previousPrice,volume,tradeTime,dailyLastPrice,dailyPriceChange,dailyOpenPrice,dailyHighPrice,dailyLowPrice,dailyPreviousPrice,dailyVolume,dailyDate1dAgo&list=futures.contractInRoot&root=VI&meta=&hasOptions=true&raw=&page=1'
        return BarchartScraper.http_get_with_retry(url)

    @staticmethod
    def parse_content(content, logger=Logger(__name__, None)):
        try:
            json_data = json.loads(content)
            for record in json_data['results']:
                yield [record['open'], record['close'], record['high'], record['low'], record['volume'],
                       #TODO: verify real time... u'2018-01-08T18:55:00-06:00'
                       datetime.strptime(record['tradeTimestamp'][0:19], '%Y-%m-%dT%H:%M:%S')]
        except Exception as e:
            logger.error('Trace: ' + traceback.format_exc(), False)
            logger.error('Error: get action arguments failed:' + str(e))
            yield [None, None, None, None, None, None]


    @staticmethod
    def get_current_data(symbols, logger=Logger(__name__, None)):
        url_template = "http://marketdata.websol.barchart.com/getQuote.json?apikey=7aa9a38e561042d48e32f3b469b730d8&symbols={}"
        url = url_template.format(','.join(symbols))
        # print url
        try:
            content = HttpHelper.http_get(url)
        except Exception as e:
            logger.error('Trace: ' + traceback.format_exc(), False)
            logger.error('Error: get action arguments failed:' + str(e))
            content = ''
        # print content
        return list(BarchartScraper.parse_content(content))


if __name__ == '__main__':
    #print WebScraper.get_expiration_dates('SPY')
    #print WebScraper.get_equity_data('SPY')
    #print WebScraper.get_option_data('SPY', '2017-07-21')
    print BarchartScraper.get_vix_data()
    #import datetime
    #print type(datetime.date.today())


