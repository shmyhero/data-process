import os
from utils.logger import Logger
from common.configmgr import ConfigMgr
from common.pathmgr import PathMgr
from optionskewdao import OptionSkewDAO
from vixdao import VIXDAO


class DataExporter(object):

    def __init__(self, daily_raw_path=None):
        self.logger = Logger(__name__, PathMgr.get_log_path())
        self.config = ConfigMgr.get_output_config()
        self.output_dir = self.config['output_dir']

    def export_skew(self):
        self.logger.info('Export skew data to csv...')
        csv_file = os.path.join(self.output_dir, self.config['skew_file'])
        OptionSkewDAO().export_data_to_csv(csv_file)
        self.logger.info('Export skew completed.')

    def export_vix(self):
        self.logger.info('Export vix data to csv...')
        vix_file = os.path.join(self.output_dir, self.config['vix_file'])
        df = VIXDAO().gen_all_vix()
        df.to_csv(vix_file)
        self.logger.info('Export vix completed.')


if __name__ == '__main__':
    #DataExporter().export_skew()
    DataExporter().export_vix()