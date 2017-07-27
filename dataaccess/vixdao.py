from dataaccess.basedao import BaseDAO


class VIXDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into vix (symbol,lastPrice,priceChange,openPrice,highPrice,lowPrice,previousPrice,volume,tradeTime,dailyLastPrice,dailyPriceChange,dailyOpenPrice,dailyHighPrice,dailyLowPrice,dailyPreviousPrice,dailyVolume,dailyDate1dAgo) values ('{}',{},{},{},{},{},{},{},'{}',{},{},{},{},{},{},{},'{}')"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        count = 0
        for vix in records:
            query = BaseDAO.mysql_format(query_template, vix.symbol, vix.lastPrice, vix.priceChange, vix.openPrice, vix.highPrice, vix.lowPrice, vix.previousPrice, vix.volume, vix.tradeTime, vix.dailyLastPrice, vix.dailyPriceChange, vix.dailyOpenPrice, vix.dailyHighPrice, vix.dailyLowPrice, vix.dailyPreviousPrice, vix.dailyVolume, vix.dailyDate1dAgo)
            self.execute_query(query, cursor)
            count += 1
            if count == 1000:
                conn.commit()
                count = 0
        conn.commit()
        conn.close()

