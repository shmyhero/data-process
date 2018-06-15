import datetime
from utils.iohelper import read_file_to_string, write_to_file
from utils.stringhelper import string_fetch
from common.pathmgr import PathMgr
from common.tradetime import TradeTime
from entities.equity import Equity
from dataaccess.equitymindao import EquityMinDAO
from dataaccess.equityrealtimedao import EquityRealTimeDAO


class QuantopianLogParser(object):

    def load_log(self, symbol, date):
        file_name = '%s%s.log'%(symbol, date.strftime('%Y%m%d'))
        path = PathMgr.get_data_path('quantopian_daily_min/%s'%file_name)
        content = read_file_to_string(path)
        lines = content.split('\n')
        filtered_lines = filter(lambda x: len(x)>100, lines)
        lines = map(lambda x: string_fetch(x, 'PRINT ', ''), filtered_lines)
        close_list_str = ','.join(lines)
        prices_list = map(float, close_list_str.split(','))
        datetimes = TradeTime.generate_datetimes(date, date)
        equities = map(lambda x, y: Equity(symbol, x, y, y, y, y), datetimes, prices_list)
        EquityMinDAO().insert(equities)

    def to_csv(self, symbol, date):
        file_name = '%s%s.log' % (symbol, date.strftime('%Y%m%d'))
        path = PathMgr.get_data_path('quantopian_daily_min/%s' % file_name)
        content = read_file_to_string(path)
        lines = content.split('\n')
        filtered_lines = filter(lambda x: len(x) > 100, lines)
        lines = map(lambda x: string_fetch(x, 'PRINT ', ''), filtered_lines)
        close_list_str = ','.join(lines)
        # print close_list_str
        prices_list = map(float, close_list_str.split(','))
        datetimes = TradeTime.generate_datetimes(date, date)
        new_lines = map(lambda x, y: '%s,%s'%(x, y), datetimes, prices_list)
        new_content = '\n'.join(new_lines)
        write_path = PathMgr.get_data_path('quantopian_daily_min/%s%s.csv' % (symbol, date.strftime('%Y%m%d')))
        write_to_file(write_path, new_content)

def realtimedata_to_csv():
    records = \
    EquityRealTimeDAO().get_min_time_and_price('SVXY',
        datetime.datetime(2018, 05, 29, 0, 0, 0),
        datetime.datetime(2018, 05, 30, 0, 0, 0),
        )
    lines = map(lambda x: '%s,%s' % (x[0], x[1]), records[1:])
    content = '\n'.join(lines)
    write_path = PathMgr.get_data_path('quantopian_daily_min/realtime_%s%s.csv' % ('SVXY', '20180529'))
    write_to_file(write_path, content)

if __name__ == '__main__':
    # date = datetime.date(2004, 11, 30)
    # QuantopianLogParser().load_log('QQQ', date)
    # date = datetime.date(2018, 05, 29)
    # QuantopianLogParser().to_csv('SVXY', date)
    realtimedata_to_csv()



