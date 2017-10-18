from utils.logger import Logger
from common.pathmgr import PathMgr
from ingestion.yahooscraper import YahooScraper
from dataaccess.yahoooptionparser import YahooOptionParser
from dataaccess.yahooequitydao import YahooEquityDAO
from aggregation.agg_spyvixhedge import AGGSPYVIXHedge


def process_for_yahoo_option_data():
    YahooScraper.ingest_all_options(['^VIX'])
    YahooOptionParser.save_to_db()
    YahooOptionParser.update_delta()

def process_for_yahoo_historical_data():
    YahooScraper.ingest_recently_historyical_etf()
    YahooEquityDAO().save_all()


def process_for_aggregation(logger):
    logger.info('run aggregations...')
    AGGSPYVIXHedge().save_to_db()
    logger.info('run aggregation completed.')


if __name__ == '__main__':
    logger = Logger(__name__, PathMgr.get_log_path())
    process_for_yahoo_option_data()
    process_for_yahoo_historical_data()
    #process_for_aggregation(logger)

