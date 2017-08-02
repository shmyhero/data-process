import traceback

from utils.logger import Logger
from common.pathmgr import PathMgr
from common.notification import notify
from ingestion.dailyingestor import DailyIngestor
from dataaccess.rawfilemgr import RawFileMgr
from dataaccess.raw2db import RawToDB
from dataaccess.dataexporter import DataExporter


def process():
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


def main():
    logger = Logger(__name__, PathMgr.get_log_path())
    try:
        process()
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





