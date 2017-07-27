import datetime
from utils.logger import Logger
from common.pathmgr import PathMgr
from dataaccess.rawdataparser import RawDataParser
from dataaccess.equitydao import EquityDAO
from dataaccess.optiondao import OptionDAO
from dataaccess.vixdao import VIXDAO


class RawToDB(object):

    def __init__(self, daily_raw_path = None):
        if daily_raw_path is None:
            daily_raw_path = PathMgr.get_data_path(str(datetime.date.today()))
        self.logger = Logger(__name__, PathMgr.get_log_path())
        self.parser = RawDataParser(daily_raw_path)
        self.parser.load_all()

    def push_to_db(self):
        self.logger.info('Push equity data to db...')
        EquityDAO().insert(self.parser.equity_records)
        self.logger.info('Push option data to db...')
        OptionDAO().insert(self.parser.option_records)
        self.logger.info('Push vix data to db...')
        VIXDAO().insert(self.parser.vix_records)



if __name__ == '__main__':
    #RawToDB(PathMgr.get_data_path()).push_to_db()
    #RawToDB(PathMgr.get_data_path('2017-07-25')).push_to_db()
    pass
