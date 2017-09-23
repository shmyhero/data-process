from basedao import BaseDAO


class SPYVIXHedgeDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def save(self, records):
        query_template = """insert into spy_vix_hedge (trade_date, vix_index, vix_delta,spy_vol,spy_price,spy_option_delta,vix_vol,vix_price,vxx_delta,ratio) values
                         (str_to_date('{}', '%Y-%m-%d'), {}, {},{},{},{},{},{},{},{})
                         on duplicate key update vix_index = {}, vix_delta = {}, spy_vol = {}, spy_price = {}, spy_option_delta = {},vix_vol = {},vix_price = {},vxx_delta = {},ratio = {}"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()

        for record in records:
            query = BaseDAO.mysql_format(query_template, record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7],record[8],record[9], \
                                         record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9])
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def select_all(self):
        query = """select * from spy_vix_hedge"""
        rows = self.select(query)
        return rows
