import traceback
import time
import pytz
from datetime import datetime
from utils.logger import Logger
from utils.listhelper import list_to_hash
from common.pathmgr import PathMgr
from dataaccess.processdao import ProcessDAO


class ProcessesInfo(object):

    def __init__(self, processes, update_process_fn):
        self.processes = processes
        self.processes_dict = list_to_hash(map(lambda x: [x, [False, None, None]], processes))
        self.update_process_fn = update_process_fn

    def get_processes(self):
        return self.processes

    def update_status(self, process, status):
        self.processes_dict[process] = status

    def start_process(self, process):
        self.processes_dict[process] = [False, datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')[0:19], None]
        self.update_process_fn(self)

    def complete_process(self, process):
        new_value = [True, self.processes_dict[process][1], datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')[0:19]]
        self.processes_dict[process] = new_value
        self.update_process_fn(self)

    def failed_process(self, process):
        new_value = [False, self.processes_dict[process][1], datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')[0:19]]
        self.processes_dict[process] = new_value
        self.update_process_fn(self)

    def to_text(self):
        return map(lambda x: [x.__name__] + self.processes_dict[x], self.processes)

    def __str__(self):
        return str(self.to_text())


class ProcessMan(object):

    def __init__(self, process_type, processes):
        self.process_type = process_type
        self.processDao = ProcessDAO()
        self.processes_info = ProcessesInfo(processes, self.update_process)
        self.logger = Logger(__name__, PathMgr.get_log_path())
        self.start_time = None

    def run_process(self, process):
        try:
            process()
            return True
        except Exception as e:
            self.logger.exception('Trace: ' + traceback.format_exc())
            self.logger.error('Error: ' + str(e))
            return False

    def update_process(self, process):
        self.processDao.update(self.process_type, self.start_time, str(self.processes_info))

    def run_all(self):
        self.start_time = datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')[0:19]
        self.processDao.insert(self.process_type, self.start_time, str(self.processes_info))
        succeed = True
        for process in self.processes_info.get_processes():
            self.processes_info.start_process(process)
            result = self.run_process(process)
            if result:
                self.processes_info.complete_process(process)
            else:
                self.processes_info.failed_process(process)
            succeed = succeed and result
        return succeed


if __name__ == '__main__':

    def foo1():
        time.sleep(1)

    def foo2():
        time.sleep(2)

    def foo3():
        time.sleep(3)

    def foo4():
        time.sleep(4)

    def foo5():
        time.sleep(5)

    fns = [foo1, foo2, foo3, foo4, foo5]
    ProcessMan('test', fns).run_all()