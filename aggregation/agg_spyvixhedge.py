import datetime
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

        symbols = VIX.get_following_symbols(datetime.datetime.now().strftime('%Y-%m-%d'))
        symbol1 = symbols[0]
        self.df1 = VIXDAO().get_vix_price_by_symbol(symbol1)
        self.dfi = VIXDAO().get_vix_price_by_symbol('VIY00')
        self.df_delta = self.df1.set_index('date').subtract(self.dfi.set_index('date'))
        self.vixf1_records = self.df1.values.tolist()
        self.vix_delta_records = map(lambda x, y: [x[0], y[0]], self.vixf1_records, self.df_delta.values.tolist())
        self.hv_vix = OptionCalculater.get_year_history_volatility_list(self.df1.values.tolist(), self.circle)
        vxx_records = YahooEquityDAO().get_all_equity_price_by_symbol('VXX', from_date_str)
        self.vxx_delta_records = self.get_delta_records('VXX', vxx_records)

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
            option_symbol = self.option_dao.find_symbol(equity_symbol, expiration_date, date_price[1], imp_only=True,
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
                           self.vixf1_records[0][0], self.vxx_delta_records[0][0], self.vix_delta_records[0][0]])
        all_dates = map(lambda r: r[0], self.spy_delta_records)
        date_list = filter(lambda x: x >= latest_date, all_dates)
        v1_list = self.get_parameter_list(self.hv_spy, latest_date)
        p1_list = self.get_parameter_list(self.spy_records, latest_date)
        d1_list = self.get_parameter_list(self.spy_delta_records, latest_date)
        v2_list = self.get_parameter_list(self.hv_vix, latest_date)
        p2_list = self.get_parameter_list(self.vixf1_records, latest_date)
        d2_list = self.get_parameter_list(self.vxx_delta_records, latest_date)
        vix_delta_list = self.get_parameter_list(self.vix_delta_records, latest_date)
        ratio_list = map(lambda v1, p1, d1, v2, p2, d2: (v1 * p1 * d1) / (v2 * p2 * d2), v1_list, p1_list, d1_list, v2_list,
                         p2_list, d2_list)
        records = map(lambda date, vix_delta, v1, p1, d1, v2, p2, d2, ratio: [date, vix_delta, v1, p1, d1, v2, p2, d2, ratio], \
                     date_list, vix_delta_list, v1_list, p1_list, d1_list, v2_list, p2_list, d2_list, ratio_list)
        return records

    def save_to_db(self):
        SPYVIXHedgeDAO().save(self.get_records())


if __name__ == "__main__":
    AGGSPYVIXHedge().save_to_db()