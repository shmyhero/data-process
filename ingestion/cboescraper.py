import datetime
from utils.stringhelper import string_fetch
from utils.httphelper import HttpHelper
from utils.iohelper import write_to_file
from common.pathmgr import PathMgr
from entities.vix import VIX
from dataaccess.vixdao import VIXDAO


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


    @staticmethod
    def parse_vix_future(item):
        title = string_fetch(item, 'title=\"', '\"')
        sub_items = item.split('<span')
        values = map(lambda x: string_fetch(x, '>', '</span>').strip('\r\n '), sub_items)
        return [title, datetime.datetime.strptime(values[1], '%m/%d/%Y').date(), float(values[2])]

    @staticmethod
    def get_vix_future():
        url = 'http://www.cboe.com/delayedquote/'
        content = HttpHelper.http_get(url)
        content = string_fetch(content, 'FutureDataTabs', 'sf_colsIn')
        items = content.split(' <a href="futures-quotes?')
        vix_items = filter(lambda x: 'VIX/' in x, items)
        return map(CBOEScraper.parse_vix_future, vix_items)

    @staticmethod
    def get_vix_records():
        futures = CBOEScraper.get_vix_future()
        records = []
        for future in futures:
            record = VIX()
            symbol = future[0].replace('X/', '')
            record.symbol = '%s1%s'%(symbol[0:3], symbol[3])
            # record.dailyDate1dAgo = future[1]
            record.dailyDate1dAgo = datetime.date.today() - datetime.timedelta(days=1)
            record.lastPrice = future[2]
            record.dailyLastPrice = future[2]
            records.append(record)
        return records

    @staticmethod
    def ingest_vix_records():
        records = CBOEScraper.get_vix_records()
        VIXDAO().insert(records)



if __name__ == '__main__':
    # CBOEScraper.get_vxmt_daily()
    # print CBOEScraper.to_yahoo_format('1/7/2008,,,,24.22')
    # print CBOEScraper.get_vix_future()
    print CBOEScraper.ingest_vix_records()

