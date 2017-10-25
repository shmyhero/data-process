import traceback
from utils.logger import Logger
from common.pathmgr import PathMgr
from common.notification import notify
from ingestion.dailyingestor import DailyIngestor
from ingestion.yahooscraper import YahooScraper
from ingestion.nyseingestor import NYSEIngestor
from ingestion.bigchartsingestor import BigChartsScraper
from dataaccess.rawfilemgr import RawFileMgr
from dataaccess.raw2db import RawToDB
from dataaccess.dataexporter import DataExporter
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahoooptionparser import YahooOptionParser
from aggregation.agg_spyvixhedge import AGGSPYVIXHedge
from processman import ProcessMan

logger = Logger(__name__, PathMgr.get_log_path())


def clean_obsoleted_data():
    RawFileMgr().clean_obsoleted_data()


def backup_daily_data():
    logger.info('backup...')
    RawFileMgr().backup()


def process_for_option_vix():
    logger.info('daily ingestion...')
    daily_ingestor = DailyIngestor()
    daily_ingestor.gen_all()
    if daily_ingestor.validate():
        RawToDB().push_to_db()
        exporter = DataExporter()
        exporter.export_skew()
        exporter.export_vix()
    else:
        raise Exception('raw data validation failed...')


def process_for_nysecredit():
    logger.info('Ingesting credit data...')
    credits = NYSEIngestor.ingest_credit()
    logger.info('Ingesting credit data completed, start to push data into database.')
    NYSECreditDAO().save(credits)
    logger.info('push credit data into database completed.')


def process_for_yahoo_option_data():
    logger.info('ingest yahoo option data...')
    YahooScraper.ingest_all_options(['^VIX'])
    YahooOptionParser.save_to_db()


def process_for_bigcharts_option_data():
    logger.info('ingest bigcharts option data...')
    BigChartsScraper.ingest_options('^VIX')


def update_option_delta():
    logger.info('update delta for vix option data...')
    YahooOptionParser.update_delta()


def process_for_yahoo_historical_data():
    logger.info('process for yahoo historial data...')
    YahooScraper.ingest_recently_historyical_etf()
    YahooEquityDAO().save_all()


def process_for_aggregation():
    logger.info('run aggregations...')
    AGGSPYVIXHedge().save_to_db()
    logger.info('run aggregation completed.')


def run():
    processes = [clean_obsoleted_data,
                 process_for_option_vix,
                 process_for_nysecredit,
                 process_for_yahoo_option_data,
                 process_for_bigcharts_option_data,
                 update_option_delta,
                 backup_daily_data,
                 process_for_yahoo_historical_data,
                 process_for_aggregation]
    return ProcessMan('data-process', processes).run_all()


def main():
    result = run()
    if result:
        logger.info('Daily ingestion completed.')
        notify('Daily data processing completed...')
    else:
        notify('Daily data processing failed...')


if __name__ == '__main__':
    main()



