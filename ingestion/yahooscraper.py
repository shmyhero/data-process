import re
import urllib2
import calendar
import datetime
import time
from utils.iohelper import write_to_file
from common.etfs import ETFS
from common.pathmgr import PathMgr
from utils.logger import Logger


class YahooScraper(object):

    crumble_cookie = None


    @staticmethod
    def get_crumble_and_cookie(symbol):
        crumble_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
        crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
        cookie_regex = r'Set-Cookie: (.*?); '
        link = crumble_link.format(symbol)
        response = urllib2.urlopen(link)
        #print response.info()
        match = re.search(cookie_regex, str(response.info()))
        cookie_str = match.group(1)
        text = response.read()
        #print text
        match = re.search(crumble_regex, text)
        crumble_str = match.group(1)
        return crumble_str, cookie_str

    @staticmethod
    def get_crumble_and_cookie_with_cache(symbol):
        if YahooScraper.crumble_cookie is None:
            YahooScraper.crumble_cookie = YahooScraper.get_crumble_and_cookie(symbol)
        return YahooScraper.crumble_cookie


    @staticmethod
    def download_quote(symbol, date_from, date_to):
        quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb={}'
        time_stamp_from = calendar.timegm(datetime.datetime.strptime(date_from, "%Y-%m-%d").timetuple())
        time_stamp_to = calendar.timegm(datetime.datetime.strptime(date_to, "%Y-%m-%d").timetuple())

        attempts = 0
        while attempts < 5:
            crumble_str, cookie_str = YahooScraper.get_crumble_and_cookie_with_cache(symbol)
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
    def ingest_all_historical_etf(date_from = '1993-01-29', date_to = datetime.date.today().strftime("%Y-%m-%d")):
        logger = Logger(__name__, PathMgr.get_log_path())
        for symbol in ETFS.get_all_symbols():
            logger.info('ingest for %s...' % symbol)
            path = PathMgr.get_historical_etf_path(symbol)
            content = YahooScraper.download_quote(symbol, date_from, date_to)
            write_to_file(path, content)
            time.sleep(1)


if __name__ == '__main__':
    #print get_crumble_and_cookie('SPY')
    #print download_quote('SPY', '2002-01-01', '2002-02-01')
    YahooScraper.ingest_all_historical_etf()


