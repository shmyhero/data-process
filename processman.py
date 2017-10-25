import traceback
from datetime import datetime
from utils.logger import Logger
from utils.listhelper import list_to_hash
from common.pathmgr import PathMgr
from processdao import ProcessDAO


class ProcessStatus(object):
    NotStart = 0
    Running = 1
    Completed = 2
    Failed = 3


class ProcessesInfo(object):

    def __init__(self, processes):
        self.processes = processes
        self.processes_dict = list_to_hash(map(lambda x: [x, ProcessStatus.NotStart], processes))

    def get_processes(self):
        return self.processes

    def update_status(self, process, status):
        self.processes_dict[process] = status

    def to_text_dict(self):
        return list_to_hash(map(lambda x, y: [x.__name__, y], self.processes_dict.keys(), self.processes_dict.values()))

    def __str__(self):
        return str(self.to_text_dict())


class ProcessMan(object):

    def __init__(self, process_type, processes):
        self.process_type = process_type
        self.processes_info = ProcessesInfo(processes)
        self.logger = Logger(__name__, PathMgr.get_log_path())
        self.processDao = ProcessDAO()
        self.start_time = None

    def run_process(self, process):
        try:
            process()
            return True
        except Exception as e:
            self.logger.exception('Trace: ' + traceback.format_exc())
            self.logger.error('Error: ' + str(e))
            return False

    def update_process(self, process, status):
        self.processes_info.update_status(process, status)
        self.processDao.update(self.process_type, self.start_time, str(self.processes_info))

    def run_all(self):
        self.start_time = datetime.now()
        self.processDao.insert(self.process_type, self.start_time, str(self.processes_info))
        succeed = True
        for process in self.processes_info.get_processes():
            self.update_process(process, ProcessStatus.Running)
            result = self.run_process(process)
            if result:
                self.update_process(process, ProcessStatus.Completed)
            else:
                self.update_process(process, ProcessStatus.Failed)
            succeed = succeed or result
        return succeed


if __name__ == '__main__':

    def foo1():
        pass

    def foo2():
        pass

    fns = [foo1, foo2]
    ProcessMan('test', fns).run_all()