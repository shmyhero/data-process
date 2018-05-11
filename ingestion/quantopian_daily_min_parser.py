import datetime
from utils.iohelper import read_file_to_string
from utils.stringhelper import string_fetch
from common.pathmgr import PathMgr
from common.tradetime import TradeTime
from entities.equity import Equity
from dataaccess.equitymindao import EquityMinDAO


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


if __name__ == '__main__':
    date = datetime.date(2004, 11, 30)
    QuantopianLogParser().load_log('QQQ', date)



