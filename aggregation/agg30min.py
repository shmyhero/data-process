import datetime
from entities.equity import Equity
from dataaccess.equitymindao import EquityMinDAO
from dataaccess.equity30mindao import Equity30MinDAO


class AGG30Min(object):

    def __init__(self):
        pass

    @staticmethod
    def combine_records(symbol, records):
        equity = Equity()
        equity.symbol = symbol
        equity.tradeTime = records[-1][0]
        equity.openPrice = records[0][1]
        equity.highPrice = max(map(lambda x:x[2], records))
        equity.lowPrice = min(map(lambda x:x[3],records))
        equity.lastPrice = records[-1][4]
        volume = sum(filter(lambda y: y is not None, map(lambda x: x[5], records)))
        if volume != 0:
            equity.volume = volume
        return equity


    @staticmethod
    def agg1to30(symbol, start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        records = EquityMinDAO().get_records(symbol, start_time, end_time)
        sub_records = []
        combined_records = []
        for record in records:
            sub_records.append(record)
            if record[0].minute%30 == 0:
                sub_records.append(record)
                combined_record = AGG30Min.combine_records(symbol, sub_records)
                combined_records.append(combined_record)
                sub_records = []
        Equity30MinDAO().insert(combined_records)


if __name__ == '__main__':
    AGG30Min.agg1to30('510050')


