import traceback
import datetime
import mysql.connector
from utils.logger import Logger
from common.pathmgr import PathMgr
from common.configmgr import ConfigMgr


class BaseDAO(object):

    def __init__(self):
        self.logger = Logger(self.__class__.__name__, PathMgr.get_log_path())

    @staticmethod
    def get_connection():
        db_config = ConfigMgr.get_db_config()
        return mysql.connector.connect(host=db_config['host'], user=db_config['user'], password=db_config['password'], database=db_config['database'])

    @staticmethod
    def python_value_to_sql_value(val):
        if val is not None:
            if type(val) is float:
                return '{:.5f}'.format(val)
            else:
                return str(val)
        else:
            return 'null'

    @staticmethod
    def mysql_format(template, *args):
        mysql_args = map(BaseDAO.python_value_to_sql_value, args)
        return template.format(*mysql_args)

    def select(self, query, cursor=None):
        #self.logger.info('query:%s' % query)
        conn = None
        if cursor is None:
            conn = BaseDAO.get_connection()
            cursor = conn.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            error_message = "Query:{}, error message: {}, Stack Trace: {}".format(query, str(e), traceback.format_exc())
            self.logger.exception(error_message)
        finally:
            if conn:
                conn.close()

    def execute_query(self, query, cursor=None):
        #self.logger.info('query:%s' % query)
        conn = None
        if cursor is None:
            conn = BaseDAO.get_connection()
            cursor = conn.cursor()
        try:
            cursor.execute(query)
            if conn:
                conn.commit()
        except mysql.connector.IntegrityError:
            pass
        except Exception as e:
            error_message = "Query:{}, error message: {}, Stack Trace: {}".format(query, str(e), traceback.format_exc())
            self.logger.exception(error_message)
        finally:
            if conn:
                conn.close()

    def execute_query_list(self, query_list):
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        try:
            query_for_log_exception = None
            for query in query_list:
                #self.logger.info('query:%s' % query)
                query_for_log_exception = query
                cursor.execute(query)
            conn.commit()
        except Exception as e:
            error_message = "Query:{}, error message: {}, Stack Trace: {}".format(query_for_log_exception, str(e), traceback.format_exc())
            self.logger.exception(error_message)
        finally:
            conn.close()

if __name__ == '__main__':
    #print BaseDAO.mysql_format('insert into table (field1, field2) values ({}, {})', None, None)
    print BaseDAO.python_value_to_sql_value(0.0)

