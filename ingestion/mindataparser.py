import datetime
from utils.iohelper import read_file_to_string
from common.pathmgr import PathMgr
from entities.equity import Equity
from dataaccess.equitymindao import EquityMinDAO


class MinDataParser(object):

    def parse_line(self, line, symbol):
        record = line.split(',')
        time = datetime.datetime.strptime('%s %s'%(record[0], record[1]), '%m/%d/%Y %H:%M')
        open_price = float(record[2])
        high_price = float(record[3])
        low_price = float(record[4])
        close_price = float(record[5])
        volume = float(record[6])
        if 9.5*60<=time.hour * 60 + time.minute <= 16*60:
            return Equity(symbol, time, open_price, high_price, low_price, close_price, close_price-open_price, volume)
        else:
            return None

    def try_parse_line(self, line, symbol):
        try:
            return self.parse_line(line, symbol)
        except Exception as e:
            print e
            print 'Error for line: %s' % line
            return None


    def load_csv(self, symbol):
        path = PathMgr.get_data_path('1mincsv/%s.txt' % symbol)
        content = read_file_to_string(path)
        lines = content.split('\n')
        return map(lambda x: self.try_parse_line(x, symbol), lines)

    def save_to_db(self, code, from_time=datetime.datetime(1990, 1, 1, 0, 0, 0)):
        records = self.load_csv(code)
        records = filter(lambda x: x is not None and x.tradeTime > from_time, records)
        count = 390
        for i in range(len(records)/count):
            sub_records = records[i*count: (i+1)*count]
            # sub_records = filter(lambda x: x is not None, sub_records)
            print sub_records[0].tradeTime
            EquityMinDAO().insert(sub_records)
        left_count = len(records)%count
        if left_count > 0:
            left_records = records[-left_count:]
            print left_records[0].tradeTime
            EquityMinDAO().insert(left_records)


if __name__ == '__main__':
    MinDataParser().save_to_db('QQQ', from_time=datetime.datetime(2005, 02, 25, 0, 0, 0))



