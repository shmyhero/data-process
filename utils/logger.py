import sys
import logging
import datetime


class Logger:

    log_file = None
    logger_names = []

    def __init__(self, name, log_path, console=True):
        self.console = console
        self.logger = logging.getLogger(name)
        if log_path:
            self.log_path = log_path
            self.logger.setLevel(logging.INFO)
            self.init_handler(name)
        else:
            self.log_path = None

    def init_handler(self, name):
        file_path = '%s/%s.log'%(self.log_path, datetime.date.today())
        if Logger.log_file != file_path:
            Logger.log_file = file_path
            Logger.logger_names = []
        if name not in Logger.logger_names:
            fh = logging.FileHandler(file_path)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            Logger.log_file = file_path
            Logger.logger_names.append(name)

    def output_console(self, customized_console):
        if customized_console is None:
            return self.console
        else:
            return customized_console

    def info(self, content, console = None):
        if self.output_console(console):
            sys.stdout.write('%s\n'%content)
        if self.log_path:
            self.logger.info(content)

    def error(self, content, console = None):
        if self.output_console(console):
            sys.stderr.write('%s\n'%content)
        if self.log_path:
            self.logger.error(content)

    def warning(self, content, console = None):
        if self.output_console(console):
            sys.stderr.write('%s\n'%content)
        if self.log_path:
            self.logger.warning(content)

    def exception(self, content, console = None):
        if self.output_console(console):
            sys.stderr.write('%s\n'%content)
        if self.log_path:
            self.logger.exception(content)