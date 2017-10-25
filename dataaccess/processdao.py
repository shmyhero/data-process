from dataaccess.basedao import BaseDAO


class ProcessDAO(BaseDAO):

    def insert(self, process_type, start_time, processes_info):
        sql_template = """insert into process (type, start_time, processes_info) values('{}', '{}', '{}')"""
        sql = sql_template.format(process_type, start_time, processes_info.replace('\'', '\\\''))
        self.execute_query(sql)

    def update(self, process_type, start_time, processes_info):
        sql_template = """update process set processes_info = '{}' where type = '{}' and start_time = '{}'"""
        sql = sql_template.format(processes_info.replace('\'', '\\\''), process_type, start_time)
        self.execute_query(sql)

    def get_latest_processes(self, process_type):
        sql_template = """select processes_info from process where type = '{}' order by start_time desc limit 1"""
        sql = sql_template.format(process_type)
        rows = self.select(sql)
        return rows[0][0]


if __name__ == '__main__':
    print ProcessDAO().get_latest_processes('test')
