import re
import urllib2
import calendar
import datetime
import time
from utils.iohelper import write_to_file
from utils.stringhelper import string_fetch
from utils.logger import Logger
from utils.httphelper import HttpHelper
from common.symbols import Symbols
from common.pathmgr import PathMgr
from common.configmgr import ConfigMgr


class YahooScraper(object):

    crumble_cookie = None


    @staticmethod
    def get_crumble_and_cookie(symbol):
        crumble_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
        crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
        cookie_regex = r'set-cookie: (.*?); '
        link = crumble_link.format(symbol)
        response = urllib2.urlopen(link)
        print response
        match = re.search(cookie_regex, str(response))
        cookie_str = match.group(1)
        text = response.read()
        #print text
        match = re.search(crumble_regex, text)
        crumble_str = match.group(1)
        return crumble_str, cookie_str

    @staticmethod
    def get_crumble_and_cookie2():
        # url_template = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
        url = 'https://finance.yahoo.com/quote/SPY'
        # content = HttpHelper.http_get(url, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        chrome_driver_path = ConfigMgr.get_others_config()['chromedriver']
        content = HttpHelper.webdriver_http_get(url, chrome_driver_path)
        # print(content)
        crumb = string_fetch(content, 'CrumbStore\":{\"crumb\":\"', '\"}')
        cookie_value = string_fetch(content, 'guid=', ';')
        cookie = 'B=%s'%cookie_value
        # print crumb, cookie
        return crumb, cookie



    @staticmethod
    def get_crumble_and_cookie_with_cache():
        if YahooScraper.crumble_cookie is None:
            YahooScraper.crumble_cookie = YahooScraper.get_crumble_and_cookie2()
        return YahooScraper.crumble_cookie



    @staticmethod
    def download_quote(symbol, date_from, date_to):
        quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb={}'
        time_stamp_from = calendar.timegm(datetime.datetime.strptime(date_from, "%Y-%m-%d").timetuple())
        time_stamp_to = calendar.timegm(datetime.datetime.strptime(date_to, "%Y-%m-%d").timetuple())

        attempts = 0
        while attempts < 5:
            crumble_str, cookie_str = YahooScraper.get_crumble_and_cookie_with_cache()
            link = quote_link.format(symbol, time_stamp_from, time_stamp_to, crumble_str)
            #print link
            #print crumble_str, cookie_str
            r = urllib2.Request(link, headers={'Cookie': cookie_str})

            try:
                response = urllib2.urlopen(r)
                text = response.read()
                #print "{} downloaded".format(symbol)
                return text
            except urllib2.URLError:
                print "{} failed at attempt # {}".format(symbol, attempts)
                attempts += 1
                time.sleep(2*attempts)
        return ""

    @staticmethod
    def download_quote2(symbol, date_from, date_to):
        url_template = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb={}'
        time_stamp_from = calendar.timegm(datetime.datetime.strptime(date_from, "%Y-%m-%d").timetuple())
        time_stamp_to = calendar.timegm(datetime.datetime.strptime(date_to, "%Y-%m-%d").timetuple())
        crumble_str, cookie = YahooScraper.get_crumble_and_cookie_with_cache()
        url = url_template.format(symbol, time_stamp_from, time_stamp_to, crumble_str)
        attempts = 0
        while attempts < 5:
            try:
                content = HttpHelper.http_get_with_time_out(url, {'Cookie':cookie})
                return content
            except urllib2.URLError:
                print "{} failed at attempt # {}".format(symbol, attempts)
                attempts += 1
                time.sleep(2 * attempts)
        return ""

    @staticmethod
    def ingest_with_retry(url):
        attempts = 0
        while attempts < 5:
            try:
                crumble_str, cookie_str = YahooScraper.get_crumble_and_cookie_with_cache()
                r = urllib2.Request(url, headers={'Cookie': cookie_str})
                response = urllib2.urlopen(r)
                text = response.read()
                # print "{} downloaded".format(symbol)
                return text
            except urllib2.URLError:
                print "{} failed at attempt # {}".format(url, attempts)
                attempts += 1
                time.sleep(2 * attempts)
        return ""

    @staticmethod
    def ingest_all_historical_etf(date_from = '1993-01-29', date_to=None, symbols=None):
        if symbols is None:
            symbols = Symbols.get_all_symbols()
        date_to = date_to or datetime.date.today().strftime("%Y-%m-%d")
        logger = Logger(__name__, PathMgr.get_log_path())
        for symbol in symbols:
            logger.info('ingest for %s...' % symbol)
            path = PathMgr.get_historical_etf_path(symbol)
            content = YahooScraper.download_quote2(symbol, date_from, date_to)
            write_to_file(path, content)
            time.sleep(1)

    @staticmethod
    def ingest_recently_historyical_etf(days=10, symbols=None):
        date_from = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        YahooScraper.ingest_all_historical_etf(date_from, symbols=symbols)

    @staticmethod
    def get_option_expirations(symbol):
        url = "https://finance.yahoo.com/quote/{}/options?p={}".format(symbol, symbol)
        content = YahooScraper.ingest_with_retry(url)
        items = string_fetch(content, '\"expirationDates\":[', ']')
        values = items.split(',')
        #content = string_fetch(content, '\"underlyingSymbol\":\"^VIX\"},', '\"sortState\":1}}}')
        #items = content.split('volume')
        #values = map(lambda x: string_fetch(x, '\"expiration\":{\"raw\":', ','), items[:-1])
        #content = string_fetch(content, 'select class=\"Fz(s)\"', '</div>')
        #items = content.split('><option')
        #values = map(lambda x: string_fetch(x, 'value=\"', '\"'),  items[1:])
        return values

    @staticmethod
    def ingest_option(symbol, date_value):
        url = "https://finance.yahoo.com/quote/{}/options?p={}&date={}".format(symbol, symbol, date_value)
        content = YahooScraper.ingest_with_retry(url)
        return content

    @staticmethod
    def ingest_all_options(symbols=Symbols.get_option_symbols()):
        logger = Logger(__name__, PathMgr.get_log_path())
        for symbol in symbols:
            logger.info('ingest option data for %s...' % symbol)
            date_values = YahooScraper.get_option_expirations(symbol)
            for date_value in date_values:
                path = PathMgr.get_yahoo_option_path(symbol, date_value)
                content = YahooScraper.ingest_option(symbol, date_value)
                write_to_file(path, content)
                time.sleep(1)
        logger.info('ingest option data completed..')

    @staticmethod
    def get_data_by_symbol(symbol):
        logger = Logger(__name__, PathMgr.get_log_path())
        yahoo_symbol = Symbols.get_mapped_symbol(symbol)
        url = 'https://finance.yahoo.com/quote/%s/' % yahoo_symbol
        logger.info('Http request to: %s' % url, False)
        content = HttpHelper.http_get(url)
        try:
            sub_content = string_fetch(content, 'Currency in USD', 'At close:')
            sub_content = string_fetch(sub_content, 'react-text', 'react-text')
            value = string_fetch(sub_content, '-->', '<!--')
            return float(value.replace(',', ''))
        except Exception:
            sub_content = string_fetch(content, '\"close\":', ',')
            value = round(float(sub_content), 2)
            return value



if __name__ == '__main__':
    #print get_crumble_and_cookie('SPY')
    #print download_quote('SPY', '2002-01-01', '2002-02-01')
    #YahooScraper.get_option_expirations('SPY')
    #print YahooScraper.ingest_all_etf_options()
    #print YahooScraper.ingest_recently_historyical_etf()
    #YahooScraper.ingest_all_historical_etf(symbols = ['^SPX'])
    # YahooScraper.ingest_all_historical_etf(symbols=['AAPL'])
    # YahooScraper.ingest_recently_historyical_etf(symbols=['^VXV'])
    # YahooScraper.ingest_all_historical_etf(symbols=['^VXX'])
    # YahooScraper.ingest_all_historical_etf(symbols=['^VXMT'])
    # YahooScraper.ingest_all_historical_etf(symbols=['VNM'])
    # YahooScraper.ingest_all_historical_etf(symbols=['ITA', 'XAR', 'FNDE', 'DGRW', 'IHI', 'BJK', 'VHT', 'CME'])
    # YahooScraper.ingest_all_historical_etf(symbols=['STZ'])
    #YahooScraper.ingest_all_historical_etf(symbols=['^GSPC', '^DJI'])
    # print YahooScraper.ingest_all_options(['^IEF'])
    # print YahooScraper.ingest_all_options(['SPY'])
    # print YahooScraper.ingest_all_options(['^VXX'])
    # print YahooScraper.get_data_by_symbol('^VIX')
    # print YahooScraper.ingest_all_options(['^VIX'])
    # YahooScraper.ingest_all_historical_etf(symbols=['ADBE', 'AVGO', 'AMZN', 'NFLX', 'GOOG'])
    # YahooScraper.ingest_all_historical_etf(symbols=['000001.SS'])
    # YahooScraper.ingest_all_historical_etf(symbols=['AIEQ'])
    # print YahooScraper.get_data_by_symbol('SVXY')

    # YahooScraper.ingest_recently_historyical_etf(symbols=['AAPL'], days=100)
    print(YahooScraper.get_crumble_and_cookie2())
    # headers = {'Cookie': u'B=e5p5f0tela0u6&b=3&s=lh'}
    # content = HttpHelper.http_get_with_time_out('https://query1.finance.yahoo.com/v7/finance/download/SPY?period1=1534262400&period2=1565798400&interval=1d&events=history&crumb=thQ7xxwmBV0', headers)
    # print(content)

