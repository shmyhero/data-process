import traceback
import time
import datetime
from utils.logger import Logger
from common.pathmgr import PathMgr
from entities.equity import Equity
from ingestion.barchartscraper import BarchartScraper
from common.tradetime import TradeTime
from dataaccess.equityrealtimedao import EquityRealTimeDAO


class RealTimeDataCollector(object):

    def __init__(self):
        self.logger = Logger(__name__, PathMgr.get_log_path('realtime'))
        self.symbols = ['XIV']  # , 'VIX', 'SVXY', 'UVXY']
        self.equity_realtime_dao = EquityRealTimeDAO()

    def collect_data(self):
        self.logger.info('ingest data for %s...' % self.symbols)
        records = BarchartScraper.get_current_data(self.symbols)
        equities = map(lambda x, y: Equity(y, x[5], x[0], x[2], x[3], x[1], None, x[4]), records, self.symbols)
        self.logger.info('save %s records into database...' % equities)
        self.equity_realtime_dao.insert(equities)

    def run(self):
        self.logger.info("start...")
        market_close_retry_count = 0
        while True:
            if TradeTime.is_market_open():
                try:
                    self.collect_data()
                except Exception as e:
                    self.logger.error('Trace: ' + traceback.format_exc())
                    self.logger.error(str(e))
            else:
                # self.logger.info('market not open sleep 1 second')
                time.sleep(1)
                market_close_retry_count = market_close_retry_count + 1
                if market_close_retry_count >= 3720: # if day light saving...
                    self.logger.info('market not open, quit...')
                    break


if __name__ == '__main__':
    # MinDataCollector().run()
    # RealTimeDataCollector().run()
    RealTimeDataCollector().collect_data()