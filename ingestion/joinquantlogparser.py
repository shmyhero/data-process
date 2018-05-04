import datetime
from utils.iohelper import read_file_to_string
from common.pathmgr import PathMgr
from entities.equity import Equity
from dataaccess.equitymindao import EquityMinDAO


class JoinQuantLogParser(object):

    def parse_line(self, line, code):
        time = datetime.datetime.strptime(line[0:19], '%Y-%m-%d %H:%M:%S')
        price = float(line[21:])
        return Equity(code, time, price, price, price, price, price, None)

    def load_log(self, code):
        path = PathMgr.get_data_path('joinquant_min/%s_2013.log'%code)
        content = read_file_to_string(path)
        lines = content.split('\n')
        filtered_lines = filter(lambda x: 'INFO' not in x and x != '', lines)
        return map(lambda x: self.parse_line(x, code), filtered_lines)

    def save_to_db(self, code):
        records = self.load_log(code)
        count = 240
        for i in range(len(records)/count):
            sub_records = records[i*count: (i+1)*count]
            print sub_records[0].tradeTime
            EquityMinDAO().insert(sub_records)

if __name__ == '__main__':
    # print JoinQuantLogParser().load_log(510050)
    JoinQuantLogParser().save_to_db(510050)



