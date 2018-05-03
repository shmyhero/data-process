import traceback
import time
from utils.logger import Logger
from common.pathmgr import PathMgr
from common.notification import notify
from ingestion.dailyingestor import DailyIngestor
from ingestion.yahooscraper import YahooScraper
from ingestion.nyseingestor import NYSEIngestor
from ingestion.bigchartsingestor import BigChartsScraper
from dataaccess.rawfilemgr import RawFileMgr
from dataaccess.raw2db import RawToDB
from dataaccess.equitymindao import EquityMinDAO
from dataaccess.equityrealtimedao import EquityRealTimeDAO
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahoooptionparser import YahooOptionParser
from aggregation.agg_spyvixhedge import AGGSPYVIXHedge
from processman import ProcessMan
from validation import Validator

logger = Logger(__name__, PathMgr.get_log_path())


def clean_obsoleted_data():
    RawFileMgr().clean_obsoleted_data()


def process_for_ingesting_barchart_data():
    logger.info('daily ingestion...')
    daily_ingestor = DailyIngestor()
    daily_ingestor.gen_all()
    if daily_ingestor.validate():
        RawToDB().push_to_db()
        #exporter = DataExporter()
        #exporter.export_skew()
        #exporter.export_vix()
    else:
        raise Exception('raw data validation failed...')


def process_for_ingesting_yahoo_option_data():
    logger.info('ingest yahoo option data...')
    YahooScraper.ingest_all_options(['^VIX'])
    YahooOptionParser.save_to_db()


def process_for_ingesting_bigcharts_option_data():
    logger.info('ingest bigcharts option data...')
    BigChartsScraper.ingest_options('VIX')


def process_for_updating_option_delta():
    logger.info('update delta for vix option data...')
    YahooOptionParser.update_delta()


def backup_daily_data():
    logger.info('backup...')
    RawFileMgr().backup()




def aggregation_for_spy_vix_hedge_table():
    logger.info('run aggregations...')
    AGGSPYVIXHedge().save_to_db()
    logger.info('run aggregation completed.')


def data_validation():
    logger.info('run caa validation...')
    Validator.validate_caa_data()
    logger.info('completed...')


def catch_up_missing_data():
    logger.info('run catch up missing_data')
    retry_count = 30  # retry for 5 hours
    for i in range(retry_count):
        symbols = YahooEquityDAO().get_missing_records_symbols()
        if len(symbols) == 0:
            break
        else:
            if i == retry_count-1:
                raise Exception('Unable to ingest missing data from yahoo website for %s times..'% retry_count)
            else:
                time.sleep(600) # sleep 10 minutes, then retry
                YahooScraper.ingest_recently_historyical_etf(symbols=symbols)
                YahooEquityDAO().save_all(symbols)
    logger.info('completed')


def add_missing_data():
    logger.info('Add missing minute data.')
    EquityMinDAO().add_missing_data()
    EquityRealTimeDAO().add_missing_data()
    logger.info('Completed.')


def save_minute_data_to_csv():
    logger.info('Save minute data.')
    EquityMinDAO().save_to_csv()
    EquityRealTimeDAO().save_to_csv()
    logger.info('Completed.')


def run():
    processes = [
                 process_for_ingesting_barchart_data,
                 process_for_ingesting_yahoo_option_data,
                 process_for_ingesting_bigcharts_option_data,
                 process_for_updating_option_delta,
                 aggregation_for_spy_vix_hedge_table,
                 # backup_daily_data,
                 # clean_obsoleted_data
                 ]
    return ProcessMan('barchart-option-process', processes).run_all()

    # for process in processes:
    #    process()


def main():
    result = run()
    if result:
        logger.info('Daily ingestion completed.')
        notify('Daily data processing completed...')
    else:
        notify('Daily data processing failed...')


if __name__ == '__main__':
    main()
    # process_for_ingesting_nyse_credit()


