import datetime
import os.path
import json
from utils.iohelper import ensure_dir_exists
from utils.iohelper import write_to_file
from utils.logger import Logger
from common.etfs import ETFS
from common.pathmgr import PathMgr
from ingestion.webscraper import WebScraper


class DailyIngestor(object):

    def __init__(self, raw_data_path = PathMgr.get_raw_data_path()):
        self.date = datetime.date.today()
        self.raw_data_path = raw_data_path
        self.daily_path = os.path.join(self.raw_data_path, str(self.date))
        self.expiration_date_dir = os.path.join(self.daily_path, 'expiration_date')
        self.equity_dir = os.path.join(self.daily_path, 'equity_data')
        self.option_data_dir = os.path.join(self.daily_path, 'option_data')
        self.vix_data_dir = os.path.join(self.daily_path, 'vix_data')
        ensure_dir_exists(self.daily_path)
        ensure_dir_exists(self.expiration_date_dir)
        ensure_dir_exists(self.equity_dir)
        ensure_dir_exists(self.option_data_dir)
        ensure_dir_exists(self.vix_data_dir)
        self.logger = Logger(__name__, PathMgr.get_log_path())

    def gen_expiration_dates(self, symbol):
        file_path = os.path.join(self.expiration_date_dir, '{}.json'.format(symbol))
        content = WebScraper.get_expiration_dates(symbol)
        write_to_file(file_path, content)
        data = json.loads(content)
        return data['meta']['expirations']

    def gen_equity_data(self, symbol):
        file_path = os.path.join(self.equity_dir, '{}.json'.format(symbol))
        content = WebScraper.get_equity_data(symbol)
        write_to_file(file_path, content)

    def gen_option_data(self, symbol, expiration_date):
        file_path = os.path.join(self.option_data_dir, '{}{}.json'.format(symbol, expiration_date))
        content = WebScraper.get_option_data(symbol, expiration_date)
        write_to_file(file_path, content)

    def gen_vix_data(self):
        file_path = os.path.join(self.vix_data_dir, 'vix.json')
        content = WebScraper.get_vix_data()
        write_to_file(file_path, content)

    def gen_all_for_symbol(self, symbol):
        expirations = self.gen_expiration_dates(symbol)
        self.gen_equity_data(symbol)
        for expiration in expirations:
            self.gen_option_data(symbol, expiration)

    def get_missing_equity_data(self):
        for symbol in ETFS.get_all_symbols():
            file_path = os.path.join(self.equity_dir, '{}.json'.format(symbol))
            if not os.path.exists(file_path):
                yield symbol

    def get_missing_expiration_data(self):
        for symbol in ETFS.get_all_symbols():
            file_path = os.path.join(self.expiration_date_dir, '{}.json'.format(symbol))
            if not os.path.exists(file_path):
                yield symbol

    def get_missing_option_data(self):
        for symbol in ETFS.get_all_symbols():
            expiration_file_path = os.path.join(self.expiration_date_dir, '{}.json'.format(symbol))
            with open(expiration_file_path) as fs:
                json_data = json.load(fs)
                expirations = json_data['meta']['expirations']
                for expiration in expirations:
                    option_file_path = os.path.join(self.option_data_dir, '{}{}.json'.format(symbol, expiration))
                    if not os.path.exists(option_file_path):
                        yield [symbol, expiration]

    def get_vix_data_count(self):
        file_path = os.path.join(self.vix_data_dir, 'vix.json')
        if not os.path.exists(file_path):
            return 0
        with open(file_path) as fs:
            json_data = json.load(fs)
            return len(json_data['data'])

    def validate(self):
        self.logger.info('Validate equity data...')
        missing_equity = list(self.get_missing_equity_data())
        if len(missing_equity) > 0:
            self.logger.error('Missing Equity data, the symbols are: %s'%missing_equity)
            return False
        else:
            self.logger.info('Equity data is ok...')
        self.logger.info('Validate expiration dates for symbol...')
        missing_expiration = list(self.get_missing_expiration_data())
        if len(missing_expiration) > 0:
            self.logger.error('Missing expiration dates for symbol, the symbols are: %s' % missing_expiration)
            return False
        else:
            self.logger.info('expiration data is ok...')
        self.logger.info('Validate option data...')
        missing_option = list(self.get_missing_option_data())
        if len(missing_option) > 0:
            self.logger.error('Missing Equity data, the symbols are: %s'%missing_option)
            return False
        else:
            self.logger.info('Option data is ok...')
        self.logger.info('Validate vix data...')
        count = self.get_vix_data_count()
        if count != 10:
            self.logger.error('The records count for vix is: %s, expect to 10.')
            return False
        else:
            self.logger.info('Vix data is ok...')
        return True

    def gen_all(self):
        for symbol in ETFS.get_all_symbols():
            self.logger.info('generate data for %s ...'%symbol)
            self.gen_all_for_symbol(symbol)
        self.logger.info('generate VIX data...')
        self.gen_vix_data()
        self.logger.info('Data ingestion completed...')



if __name__ == '__main__':
    daily_ingestor = DailyIngestor('/Users/tradehero/python-projects/data-process/data')
    #daily_ingestor.gen_all()
    #daily_ingestor.gen_vix_data()
    #print ETFS.get_all_symbols()
    #daily_ingestor.gen_equity_data('XOP')
    daily_ingestor.validate()









