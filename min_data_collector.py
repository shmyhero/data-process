import traceback
import time
import datetime
from utils.logger import Logger
from common.pathmgr import PathMgr
from ingestion.alphavantage import AlphaVantage
from dataaccess. equitymindao import EquityMinDAO
from common.tradetime import TradeTime


class MinDataCollector(object):

    def __init__(self):
        self.logger = Logger(__name__, PathMgr.get_log_path('minutes'))
        self.alpha_vantage = AlphaVantage()
        self.equity_min_dao = EquityMinDAO()
        self.symbols = ['SPX', 'XIV', 'VIX', 'SVXY', 'UVXY']

    def collect_data(self):
        for symbol in self.symbols:
            self.logger.info('ingest data for %s...'% symbol)
            equities = self.alpha_vantage.get_minutes_equites(symbol)
            self.logger.info('save %s records into database...' % symbol)
            self.equity_min_dao.insert(equities)
            time.sleep(1)

    def run(self):
        self.logger.info("start...")
        while True:
            if TradeTime.is_market_open() or datetime.datetime.now().minute == 0:
                try:
                    self.collect_data()
                except Exception as e:
                    self.logger.error('Trace: ' + traceback.format_exc())
                    self.logger.error(str(e))
            else:
                time.sleep(1)


if __name__ == '__main__':
    # MinDataCollector().run()
    MinDataCollector().collect_data()