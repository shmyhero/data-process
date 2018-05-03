from dataaccess.basedao import BaseDAO


class Equity30MinDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into equity_30min (symbol,tradeTime,openPrice,highPrice,lowPrice,closePrice,volume)
                            values ('{}','{}',{},{},{},{},{})
                            on duplicate key update openPrice={},highPrice={},lowPrice={},closePrice={},volume={}
                         """
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        for equity in records:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.volume, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()
