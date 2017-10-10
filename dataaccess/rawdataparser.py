import os.path
import json
import datetime
import glob
from common.symbols import Symbols
from common.pathmgr import PathMgr
from entities.equity import Equity
from entities.option import Option
from entities.vix import VIX


class RawDataParser(object):

    def __init__(self, daily_raw_path):
        self.daily_path = daily_raw_path
        self.equity_records = []
        self.option_records = []
        self.vix_records = []

    def load_equity_data_by_symbol(self, symbol):
        file_path = os.path.join(self.daily_path, 'equity_data', '{}.json'.format(symbol))
        with open(file_path) as fs:
            json_data = json.load(fs)
        equity = Equity.loads(json_data['data'][0])
        return equity

    def load_option_data_by_symbol(self, symbol, trade_time):
        sub_path = os.path.join(self.daily_path, 'option_data', '{}2*.json'.format(symbol))
        file_path_list = glob.glob(sub_path)
        for file_path in file_path_list:
            with open(file_path) as fs:
                json_data = json.load(fs)
                for record in json_data['data']:
                    option = Option.loads(record)
                    option.underlingSymbol = symbol
                    option.tradeTime = trade_time
                    yield option

    def load_vix_data_by(self):
        file_path = os.path.join(self.daily_path, 'vix_data', 'vix.json')
        with open(file_path) as fs:
            json_data = json.load(fs)
            for record in json_data['data']:
                vix = VIX.loads(record)
                yield vix

        #with open(file_path) as fs:
        #    json_data = json.load(fs)
        #equity = Equity.loads(json_data['data'][0])
        #return equity

    def load_all(self):
        for symbol in Symbols.get_option_symbols():
            equity = self.load_equity_data_by_symbol(symbol)
            self.equity_records.append(equity)
            option_list = list(self.load_option_data_by_symbol(symbol, equity.tradeTime))
            self.option_records.extend(option_list)
        self.vix_records = list(self.load_vix_data_by())




if __name__ == '__main__':
    #parser = RawDataParser(PathMgr.get_data_path(str(datetime.date.today())));
    parser = RawDataParser(PathMgr.get_raw_data_path('2017-10-10'));
    #parser.load_equity_data_by_symbol('UNG')
    #parser.load_option_data_by_symbol('UNG')
    #vix_list = list(parser.load_vix_data_by_symbol())
    #print len(vix_list)
    #print vix_list[8].to_json()
    #parser.load_all()
    #print parser.vix_records
    records = list(parser.load_vix_data_by())
    from dataaccess.vixdao import VIXDAO
    VIXDAO().insert(records)

