import traceback
import time
import datetime
import pytz
from utils.logger import LoggerFactory
from common.pathmgr import PathMgr
from entities.equity import Equity
from ingestion.webscraper import YahooScraper, MarketWatchScraper
from common.tradetime import TradeTime
from dataaccess.equityrealtimedao import EquityRealTimeDAO


class RealTimeDataCollector(object):

    def __init__(self):
        self.symbol = 'SVXY'  # , 'VIX', 'SVXY', 'UVXY']
        self.equity_realtime_dao = EquityRealTimeDAO()

    @property
    def logger(self):
        return LoggerFactory.create_daily_logger(__name__, PathMgr.get_log_path('realtime'))

    def collect_data(self):
        self.logger.info('ingest data for %s...' % self.symbol)
        us_dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
        price = None
        try:
            price = YahooScraper().get_current_data(self.symbol)
        except Exception as e:
            self.logger.exception(str(e))
        if price is None:
            try:
                price = MarketWatchScraper().get_current_data(self.symbol)
            except Exception as e:
                self.logger.exception(str(e))
        if price is not None:
            self.logger.info('save record into database...')
            self.equity_realtime_dao.insert(self.symbol, us_dt, price)
        else:
            self.logger.info('ingest record failed at %s...' % us_dt)

    def run(self):
        self.logger.info("start...")
        while True:
            if TradeTime.is_market_open():
                try:
                    self.collect_data()
                    self.logger.info('Check missing data...')
                    count = self.equity_realtime_dao.add_missing_data_in_real_time()
                    if count is not None and count > 0:
                        self.logger.info('Filled {} records...'.format(count))
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