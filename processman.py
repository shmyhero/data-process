import traceback
from datetime import datetime
from utils.logger import Logger
from utils.listhelper import list_to_hash
from common.pathmgr import PathMgr
from processdao import ProcessDAO


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
        self.processes_dict[process] = [False, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None]
        self.update_process_fn(self)

    def complete_process(self, process):
        new_value = [True, self.processes_dict[process][1], datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        self.processes_dict[process] = new_value
        self.update_process_fn(self)

    def failed_process(self, process):
        new_value = [False, self.processes_dict[process][1], datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        self.processes_dict[process] = new_value
        self.update_process_fn(self)

    def to_text_dict(self):
        return list_to_hash(map(lambda x, y: [x.__name__, y], self.processes_dict.keys(), self.processes_dict.values()))

    def __str__(self):
        return str(self.to_text_dict())


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
        self.start_time = datetime.now()
        self.processDao.insert(self.process_type, self.start_time, str(self.processes_info))
        succeed = True
        for process in self.processes_info.get_processes():
            self.processes_info.start_process(process)
            result = self.run_process(process)
            if result:
                self.processes_info.complete_process(process)
            else:
                self.processes_info.failed_process(process)
            succeed = succeed or result
        return succeed


if __name__ == '__main__':

    def foo1():
        pass

    def foo2():
        pass

    fns = [foo1, foo2]
    ProcessMan('test', fns).run_all()