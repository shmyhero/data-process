import os.path
import datetime
from utils.iohelper import ensure_dir_exists


class PathMgr(object):

    def __init__(self):
        pass

    @staticmethod
    def get_project_path():
        path_dir = os.path.dirname(os.path.abspath(__file__))
        return path_dir[:path_dir.rindex(os.path.sep)]

    @staticmethod
    def get_config_path():
        project_path = PathMgr.get_project_path()
        return os.path.join(project_path, 'config.conf')

    @staticmethod
    def get_log_path(sub_path = None):
        project_path = PathMgr.get_project_path()
        if sub_path:
            log_path = os.path.join(project_path, "logs", sub_path)
        else:
            log_path = os.path.join(project_path, "logs")
        ensure_dir_exists(log_path)
        return log_path

    @staticmethod
    def get_data_path(sub_path = None):
        project_path = PathMgr.get_project_path()
        if sub_path:
            data_path = os.path.join(project_path, "data", sub_path)
        else:
            data_path = os.path.join(project_path, "data")
        return data_path

    @staticmethod
    def get_raw_data_path(sub_path = None):
        raw_path = PathMgr.get_data_path('raw')
        if sub_path:
            data_path = os.path.join(raw_path, sub_path)
        else:
            return raw_path
        return data_path

    @staticmethod
    def get_historical_etf_path(symbol=None):
        historical_path = PathMgr.get_data_path('historical')
        if symbol:
            etf_path = os.path.join(historical_path, 'ETFS', symbol + '.csv')
        else:
            etf_path = os.path.join(historical_path, 'ETFS')
        return etf_path

    @staticmethod
    def get_yahoo_option_dir(sub_path = datetime.date.today().strftime('%Y-%m-%d')):
        raw_date_dir = PathMgr.get_raw_data_path(sub_path)
        yahoo_option_dir = os.path.join(raw_date_dir, 'yahoo_option')
        ensure_dir_exists(yahoo_option_dir)
        return yahoo_option_dir

    @staticmethod
    def get_yahoo_option_symbol_dir(symbol,  sub_path= datetime.date.today().strftime('%Y-%m-%d')):
        option_path = PathMgr.get_yahoo_option_dir(sub_path)
        return os.path.join(option_path, symbol)

    @staticmethod
    def get_yahoo_option_path(symbol, date_value):
        symbol_path = os.path.join(PathMgr.get_yahoo_option_dir(), symbol)
        ensure_dir_exists(symbol_path)
        return os.path.join(symbol_path, date_value + '.html')

    @staticmethod
    def get_bigcharts_option_dir(sub_path = datetime.date.today().strftime('%Y-%m-%d')):
        raw_date_dir = PathMgr.get_raw_data_path(sub_path)
        bigcharts_option_dir = os.path.join(raw_date_dir, 'bigcharts_option')
        ensure_dir_exists(bigcharts_option_dir)
        return bigcharts_option_dir

    @staticmethod
    def get_bigcharts_option_symbol_path(symbol,  sub_path= datetime.date.today().strftime('%Y-%m-%d')):
        option_path = PathMgr.get_bigcharts_option_dir(sub_path)
        return os.path.join(option_path, symbol + '.html')

