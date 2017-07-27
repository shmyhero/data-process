import datetime
import os.path
import shutil
from utils.shell import Shell
from utils.logger import Logger
from utils.iohelper import get_sub_dir_names
from common.pathmgr import PathMgr
from common.configmgr import ConfigMgr
from utils.s3helper import S3


class RawFileMgr(object):
    """
    raw data management
    """

    def __init__(self):
        self.logger = Logger(__name__, PathMgr.get_log_path())

    @staticmethod
    def zip_raw_data(folder_name = str(datetime.date.today()), logger = Logger(None, None, True)):
        folder_path = PathMgr.get_data_path(folder_name)
        file_path = os.path.join(PathMgr.get_data_path(), folder_name + '.zip')
        logger.info('zip file form {} to {}...'.format(folder_path, file_path))
        Shell.zip(folder_path, file_path)
        return file_path

    @staticmethod
    def backup_to_s3(file_path, logger = Logger(None, None, True)):
        s3_config = ConfigMgr.get_s3_config()
        file_name = os.path.basename(file_path)
        s3_key = s3_config['raw_key'] + file_name
        logger.info('upload file from {} to {}...'.format(file_path, s3_key))
        S3(s3_config['bucket']).upload_file(file_path, s3_key)

    def backup(self, folder_name = str(datetime.date.today())):
        file_path = RawFileMgr.zip_raw_data(folder_name, self.logger)
        RawFileMgr.backup_to_s3(file_path, self.logger)
        self.logger.info('remove local zip file {} ...'.format(file_path))
        os.remove(file_path)

    def clean_obsoleted_data(self, hold_days = 3):
        self.logger.info('remove raw files {} days agao ...'.format(hold_days))
        date = datetime.datetime.now() - datetime.timedelta(hold_days)
        start_date = date.date().strftime('%Y-%m-%d')
        data_path = PathMgr.get_data_path()
        sub_dir_names = get_sub_dir_names(data_path)
        for dir_name in sub_dir_names:
            if dir_name < start_date:
                dir_path = os.path.join(data_path, dir_name)
                self.logger.info('Remove obsoleted data on: {}'.format(dir_path))
                shutil.rmtree(dir_path)


if __name__ == '__main__':
    RawFileMgr().clean_obsoleted_data()





