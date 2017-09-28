import datetime
from utils.listhelper import list_to_hash
from common.tradetime import TradeTime
from common.optioncalculater import OptionCalculater
from entities.vix import VIX
from dataaccess.basedao import BaseDAO
from dataaccess.optiondao import OptionDAO
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.vixdao import VIXDAO
from dataaccess.spyvixhedgedao import SPYVIXHedgeDAO

# ratio = (V1 * P1 * D1) / (V2 * P2 * D2)
# V: 20 days historical volatility, v1: spy etf hv, p2: vix fist month hv
# P: price, P1: spy price, P2:VIX first month price
# D: D1: SPY first month option's delta, D2: VXX fist month option's delta..
# VIX delta: VIX first month future pirce - VIX index price.


class AGGSPYVIXHedge(object):

    def __init__(self):
        self.circle = 20
        self.option_dao = OptionDAO()

        # get the equity records from 100 date ago.
        from_date_str = (datetime.date.today() - datetime.timedelta(100)).strftime('%Y-%m-%d')
        self.spy_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str)
        self.hv_spy = OptionCalculater.get_year_history_volatility_list(self.spy_records, self.circle)
        self.spy_delta_records = self.get_delta_records('SPY', self.spy_records)

        from_date = TradeTime.get_latest_trade_date() - datetime.timedelta(50)
        self.vix_index_records = VIXDAO().get_vix_price_by_symbol_and_date('VIY00', from_date=from_date)
        (records_f1, records_f2) = VIXDAO().get_following_vix(from_date)
        self.vixf1_records = records_f1
        self.vix_delta_records = map(lambda x, y: [x[0], y[1]-x[1]], self.vix_index_records, self.vixf1_records)
        self.hv_vix = list(self.calculate_f1_volatilities())
        vxx_records = YahooEquityDAO().get_all_equity_price_by_symbol('VXX', from_date_str)
        self.vxx_delta_records = self.get_delta_records('VXX', vxx_records)

    def calculate_f1_volatilities(self):
        symbols = list(set(map(lambda x: x[2], self.vixf1_records)))
        symbol_dic = {}
        for symbol in symbols:
            symbol_records = VIXDAO().get_vix_price_by_symbol_and_date(symbol, self.vixf1_records[0][0])
            hv_dic = list_to_hash(OptionCalculater.get_year_history_volatility_list(symbol_records, self.circle))
            symbol_dic[symbol] = hv_dic
        for vix_f1_record in self.vixf1_records[20:]:
            date = vix_f1_record[0]
            symbol = vix_f1_record[2]
            hv = symbol_dic[symbol].get(date)
            yield [date, hv]

    def find_following_expiration_date(self, dates, current_date):
        filtered_dates = filter(lambda x: x > current_date, dates)
        for d in filtered_dates:
            if d.weekday() == 4 and 14 < d.day < 22:
                return d

    def get_delta_records(self, equity_symbol, equity_records, days_to_current_date=10):
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        delta_list = []
        # hard code here, because the option was ingested from 20170724, and some vxx data may wrong before (or on) 20170824
        filtered_equity_records = filter(lambda x: x[0] >= datetime.date(2017, 8, 24), equity_records)
        all_unexpired_dates = self.option_dao.get_all_unexpired_dates(equity_symbol, filtered_equity_records[0][0],
                                                                      cursor=cursor)
        for date_price in filtered_equity_records:
            expiration_date = self.find_following_expiration_date(all_unexpired_dates, date_price[0])
            # expiration_date = self.option_dao.get_following_expirationDate(equity_symbol, date_price[0])
            option_symbol = self.option_dao.find_symbol(equity_symbol, expiration_date, date_price[1], imp_only=True, current_date=date_price[0],
                                                        days_to_current_date=days_to_current_date, cursor=cursor)
            delta = self.option_dao.get_delta_by_symbol_and_date(option_symbol, date_price[0], cursor)
            if delta is not None:
                delta_list.append([date_price[0], delta])
        conn.commit()
        conn.close()
        return delta_list

    def get_parameter_list(self, records, latest_date):
        filtered_records = filter(lambda x: x[0] >= latest_date, records)
        values = map(lambda x: x[1], filtered_records)
        # fix the wrong data, the vix option data records is not correct on 20170823.
        previous_value = None
        fixed_values = []
        for value in values:
            if value is None:
                value = previous_value
            previous_value = value
            fixed_values.append(value)
        return fixed_values


    def get_records(self):
        latest_date = max([self.spy_records[0][0], self.hv_spy[0][0], self.spy_delta_records[0][0], self.hv_vix[0][0],
                           self.vixf1_records[0][0], self.vxx_delta_records[0][0], self.vix_index_records[0][0], self.vix_delta_records[0][0]])
        all_dates = map(lambda r: r[0], self.spy_delta_records)
        date_list = filter(lambda x: x >= latest_date, all_dates)
        v1_list = self.get_parameter_list(self.hv_spy, latest_date)
        p1_list = self.get_parameter_list(self.spy_records, latest_date)
        d1_list = self.get_parameter_list(self.spy_delta_records, latest_date)
        v2_list = self.get_parameter_list(self.hv_vix, latest_date)
        p2_list = self.get_parameter_list(self.vixf1_records, latest_date)
        d2_list = self.get_parameter_list(self.vxx_delta_records, latest_date)
        vix_index_list = self.get_parameter_list(self.vix_index_records, latest_date)
        vix_delta_list = self.get_parameter_list(self.vix_delta_records, latest_date)
        ratio_list = map(lambda v1, p1, d1, v2, p2, d2: (v1 * p1 * d1) / (v2 * p2 * d2), v1_list, p1_list, d1_list, v2_list,
                         p2_list, d2_list)
        records = map(lambda date, vix_index, vix_delta, v1, p1, d1, v2, p2, d2, ratio: [date, vix_index, vix_delta, v1, p1, d1, v2, p2, d2, ratio], \
                     date_list, vix_index_list, vix_delta_list, v1_list, p1_list, d1_list, v2_list, p2_list, d2_list, ratio_list)
        return records

    def save_to_db(self):
        SPYVIXHedgeDAO().save(self.get_records())


if __name__ == "__main__":
    AGGSPYVIXHedge().save_to_db()