import datetime
from utils.stringhelper import string_fetch
from utils.httphelper import HttpHelper
from utils.iohelper import write_to_file
from common.pathmgr import PathMgr


class CBOEScraper(object):

    @staticmethod
    def to_yahoo_format(line):
        (date_str, open_price, high_price, low_price, close_price)= line.split(',')
        yahoo_date_str = datetime.datetime.strptime(date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
        if open_price == '':
            open_price = close_price
        if high_price == '':
            high_price = close_price
        if low_price == '':
            low_price = close_price
        yahoo_line = '{},{},{},{},{},{},0'.format(yahoo_date_str, open_price, high_price, low_price, close_price, close_price)
        return yahoo_line


    @staticmethod
    def get_vxmt_daily():
        url = 'http://www.cboe.com/publish/ScheduledTask/MktData/datahouse/vxmtdailyprices.csv'
        content = HttpHelper.http_get(url)
        records = content.split('\r\n')[3:-1]
        yahoo_records = ['Date,Open,High,Low,Close,Adj Close,Volume'] + map(CBOEScraper.to_yahoo_format, records)
        yahoo_content = '\r\n'.join(yahoo_records)
        path = PathMgr.get_historical_etf_path('^VXMT')
        write_to_file(path, yahoo_content)


if __name__ == '__main__':
    CBOEScraper.get_vxmt_daily()
    # print CBOEScraper.to_yahoo_format('1/7/2008,,,,24.22')


