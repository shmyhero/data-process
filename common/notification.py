import datetime
from utils.mail import sendmail
from utils.iohelper import read_file_to_string
from common.pathmgr import PathMgr
from common.configmgr import ConfigMgr


def notify(subject, log_file = None):
    if log_file is None:
        log_file = PathMgr.get_log_path('%s.log'%str(datetime.date.today()))
    mail_config = ConfigMgr.get_mail_config()
    sendmail(mail_config['smtp_server'], mail_config['sender'], mail_config['sender_password'], mail_config['receiver'], subject, log_file)