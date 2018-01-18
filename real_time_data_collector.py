import traceback
import time
import datetime
import pytz
from utils.logger import Logger
from common.pathmgr import PathMgr
from entities.equity import Equity
from ingestion.webscraper import YahooScraper
from common.tradetime import TradeTime
from dataaccess.equityrealtimedao import EquityRealTimeDAO


class RealTimeDataCollector(object):

    def __init__(self):
        self.logger = Logger(__name__, PathMgr.get_log_path('realtime'))
        self.symbol = 'XIV'  # , 'VIX', 'SVXY', 'UVXY']
        self.equity_realtime_dao = EquityRealTimeDAO()
        self.webScraper = YahooScraper()

    def collect_data(self):
        self.logger.info('ingest data for %s...' % self.symbol)
        us_dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
        price = self.webScraper.get_current_data(self.symbol)
        self.logger.info('save record into database...')
        self.equity_realtime_dao.insert(self.symbol, us_dt, price)

    def run(self):
        self.logger.info("start...")
        while True:
            if TradeTime.is_market_open():
                try:
                    self.collect_data()
                except Exception as e:
                    self.logger.error('Trace: ' + traceback.format_exc())
                    self.logger.error(str(e))
            else:
                self.logger.info('market not open...')
            time.sleep(10)


if __name__ == '__main__':
    # MinDataCollector().run()
    RealTimeDataCollector().run()
    # RealTimeDataCollector().collect_data()