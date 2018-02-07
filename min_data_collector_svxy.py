import traceback
import time
import datetime
from utils.logger import Logger
from common.pathmgr import PathMgr
from ingestion.alphavantage import AlphaVantage
from dataaccess. equitymindao import EquityMinDAO
from common.tradetime import TradeTime


class MinDataCollectorSVXY(object):

    def __init__(self):
        self.logger = Logger(__name__, PathMgr.get_log_path('minutes'))
        self.alpha_vantage = AlphaVantage()
        self.equity_min_dao = EquityMinDAO()

    def collect_data(self):
        symbol = 'SVXY'
        self.logger.info('ingest data for %s...'% symbol)
        equities = self.alpha_vantage.get_minutes_equites(symbol)
        self.logger.info('save %s records into database...' % symbol)
        self.equity_min_dao.insert(equities)

    def run(self):
        self.collect_data()
        self.logger.info('Check missing data...')
        count = self.equity_min_dao.add_missing_data_in_real_time()
        if count is not None and count > 0:
            self.logger.info('Filled {} records...'.format(count))


if __name__ == '__main__':
    MinDataCollectorSVXY().run()