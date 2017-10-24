from dataaccess.basedao import BaseDAO


class ProcessDAO(BaseDAO):

    def insert(self, process_type, start_time):
        sql_template = """insert into process (type, start_time) values('{}', '{}')"""
        sql = sql_template.format(process_type, start_time)
        self.execute_query(sql)

    def update(self, process_type, start_time, steps):
        sql_template = """update process set steps = '{}' where type = '{}' and start_time = '{}'"""
        sql = sql_template.format(steps, process_type, start_time)
        self.execute_query(sql)
