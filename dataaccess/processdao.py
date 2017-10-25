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

