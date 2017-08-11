import traceback

from utils.logger import Logger
from common.pathmgr import PathMgr
from common.notification import notify
from ingestion.dailyingestor import DailyIngestor
from ingestion.yahooscraper import YahooScraper
from ingestion.nyseingestor import NYSEIngestor
from dataaccess.rawfilemgr import RawFileMgr
from dataaccess.raw2db import RawToDB
from dataaccess.dataexporter import DataExporter
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.nysecreditdao import NYSECreditDAO


def process_for_option_vix():
    raw_file_mgr = RawFileMgr()
    raw_file_mgr.clean_obsoleted_data()
    daily_ingestor = DailyIngestor()
    daily_ingestor.gen_all()
    if daily_ingestor.validate():
        raw_file_mgr.backup()
        RawToDB().push_to_db()
        exporter = DataExporter()
        exporter.export_skew()
        exporter.export_vix()
    else:
        raise Exception('raw data validation failed...')


def process_for_yahoo_data():
    YahooScraper.ingest_all_historical_etf()
    YahooEquityDAO().save_all()

def process_for_nysecredit():
    credits = NYSEIngestor.ingest_credit()
    NYSECreditDAO().save(credits)


def main():
    logger = Logger(__name__, PathMgr.get_log_path())
    try:
        process_for_option_vix()
        process_for_nysecredit()
        process_for_yahoo_data()
        return True
    except Exception as e:
        logger.exception('Trace: ' + traceback.format_exc())
        logger.error('Error: ' + str(e))
        return False


if __name__ == '__main__':
    result = main()
    #result = True
    if result:
        notify('Daily data processing completed...')
    else:
        notify('Daily data processing failed...')





