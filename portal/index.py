import web
import datetime
import cStringIO
import sys
import json
from abc import abstractmethod
from utils.querystringparser import parse_query_string
from common.etfs import ETFS
from common.optioncalculater import OptionCalculater
from entities.vix import VIX
from dataaccess.basedao import BaseDAO
from dataaccess.equitydao import EquityDAO
from dataaccess.vixdao import VIXDAO
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.optiondao import OptionDAO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


render = web.template.render('portal/templates')


class Index:

    def GET(self):
        #return """<a href=\"credit\">credit</a>"""
        return render.index()


class VixAll:

    def GET(self):
        return render.vix()


class PlotPoint:

    def GET(self):
        fig = Figure(figsize=[4, 4])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.scatter([1, 2], [3, 4])
        canvas = FigureCanvasAgg(fig)

        # write image data to a string buffer and get the PNG image bytes
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class Credit:

    def GET(self):
        credits_df = NYSECreditDAO().get_all_margin_debt()
        spy_df = YahooEquityDAO().get_equity_monthly_by_symbol('SPY', ['lastdate', 'adjcloseprice'])
        dates = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), credits_df['lastDate'])
        debt = credits_df['margin_debt']
        spy_prices = spy_df['adjcloseprice'][0:len(dates)]
        fig = Figure(figsize=[12, 8])
        ax1 = fig.add_axes([.1, .1, .8, .8])
        ax2 = ax1.twinx()
        ax1.plot(dates, debt, 'r-', label='credit margin debt')
        ax2.plot(dates, spy_prices, 'b-', label='SPY')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper center')
        canvas = FigureCanvasAgg(fig)

        # write image data to a string buffer and get the PNG image bytes
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class VIXBase(object):

    def __init__(self):
        pass

    @abstractmethod
    def get_symbol(self):
        return None

    @abstractmethod
    def get_label(self):
        return None

    def get_plot_data(self):
        symbol = self.get_symbol()
        df = VIXDAO().get_vix_price_by_symbol(symbol)
        dates = df['date']
        price = df['price']
        fig = Figure(figsize=[12, 8])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, price, label=self.get_label())
        ax.legend(loc='upper left')
        ax.grid()
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class VIXIndex(VIXBase):

    def __init__(self):
        VIXBase.__init__(self)

    def get_symbol(self):
        return 'VIY00'

    def get_label(self):
        return 'VIX Index'

    def GET(self):
        return self.get_plot_data()


class VIXF1(VIXBase):

    def __init__(self):
        VIXBase.__init__(self)

    def get_symbol(self):
        symbols = VIX.get_following_symbols(datetime.datetime.now().strftime('%Y-%m-%d'))
        return list(symbols)[0]

    def get_label(self):
        return 'VIX First Month'

    def GET(self):
        return self.get_plot_data()


class VIXF2(VIXBase):

    def __init__(self):
        VIXBase.__init__(self)

    def get_symbol(self):
        symbols = VIX.get_following_symbols(datetime.datetime.now().strftime('%Y-%m-%d'))
        return list(symbols)[1]

    def get_label(self):
        return 'VIX Second Month'

    def GET(self):
        return self.get_plot_data()


class VIX3in1(object):

    def __init__(self):
        pass

    def GET(self):
        dfs = VIXDAO().get3vix()
        dates = dfs[0]['date']
        price_index = dfs[0]['price']
        price_f1 = dfs[1]['price']
        price_f2 = dfs[2]['price']
        fig = Figure(figsize=[12, 8])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, price_index, label='vix index')
        ax.plot(dates, price_f1, label='vix first month')
        ax.plot(dates, price_f2, label='vix second month')
        ax.legend(loc='upper left')
        ax.grid()
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class SPYVIXHedge(object):

    def __init__(self):
        self.circle = 20
        self.option_dao = OptionDAO()

        # get the equity records from 100 date ago.
        from_date_str = (datetime.date.today() - datetime.timedelta(100)).strftime('%Y-%m-%d')
        self.spy_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date_str)
        #current_spy_price = self.spy_records[-1][1]
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


        #self.vxx_delta_records = OptionDAO().get_corresponding_delta('VXX', vxx_records[-1][1], days_to_current_date=10)

        #first_tradetime = self.df1.iloc[0][0]
        #self.spy_records = self.yahooEquityDAO.get_all_equity_price_by_symbol('SPY', first_tradetime.strftime('%Y-%m-%d'))
        #self.spy_delta_list = self.get_delta_list('SPY', self.spy_records)

    def find_following_expiration_date(self, dates, current_date):
        filtered_dates = filter(lambda x: x > current_date, dates)
        for d in filtered_dates:
            if d.weekday() == 4 and 14 < d.day < 22:
                return d

    def get_delta_records(self, equity_symbol, equity_records, days_to_current_date = 10):
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        delta_list = []
        # hard code here, because the option was ingested from 20170724, and some vxx data may wrong before (or on) 20170824
        filtered_equity_records = filter(lambda x: x[0] >= datetime.date(2017, 8, 24), equity_records)
        all_unexpired_dates = self.option_dao.get_all_unexpired_dates(equity_symbol, filtered_equity_records[0][0], cursor= cursor)
        for date_price in filtered_equity_records:
            expiration_date = self.find_following_expiration_date(all_unexpired_dates, date_price[0])
            #expiration_date = self.option_dao.get_following_expirationDate(equity_symbol, date_price[0])
            option_symbol = self.option_dao.find_symbol(equity_symbol, expiration_date, date_price[1], imp_only=True, days_to_current_date= days_to_current_date, cursor=cursor)
            delta = self.option_dao.get_delta_by_symbol_and_date(option_symbol, date_price[0], cursor)
            if delta is not None:
                delta_list.append([date_price[0], delta])
        conn.commit()
        conn.close()
        return delta_list


    def get_parameter_list(self, records, latest_date):
        filtered_records = filter(lambda x: x[0] >= latest_date, records)
        values = map(lambda x: x[1], filtered_records)
        #fix the wrong data, the vix option data records is not correct on 20170823.
        previous_value = None
        fixed_values = []
        for value in values:
            if value is None:
                value = previous_value
            previous_value = value
            fixed_values.append(value)
        return fixed_values

    def get_report(self):
        latest_date = max([self.spy_records[0][0], self.hv_spy[0][0], self.spy_delta_records[0][0], self.hv_vix[0][0], self.vixf1_records[0][0], self.vxx_delta_records[0][0], self.vix_delta_records[0][0]])
        all_dates = map(lambda r: r[0], self.spy_delta_records)
        date_list = filter(lambda x : x >= latest_date, all_dates)
        v1_list = self.get_parameter_list(self.hv_spy, latest_date)
        p1_list = self.get_parameter_list(self.spy_records, latest_date)
        d1_list = self.get_parameter_list(self.spy_delta_records, latest_date)
        v2_list = self.get_parameter_list(self.hv_vix, latest_date)
        p2_list = self.get_parameter_list(self.vixf1_records, latest_date)
        d2_list = self.get_parameter_list(self.vxx_delta_records, latest_date)
        vix_delta_list = self.get_parameter_list(self.vix_delta_records, latest_date)
        ratio_list = map(lambda v1, p1, d1, v2, p2, d2: (v1 * p1 * d1)/(v2 * p2 * d2), v1_list, p1_list, d1_list, v2_list, p2_list,d2_list)
        report = map(lambda date, vix_delta, v1, p1, d1, v2, p2, d2,ratio : [date, vix_delta, v1, p1, d1, v2, p2, d2, ratio], \
                     date_list, vix_delta_list, v1_list, p1_list, d1_list, v2_list, p2_list, d2_list, ratio_list)
        return report

    def GET(self):
        report_data = self.get_report()
        return render.spyvixhedge(report_data)

    def GET_obsoleted(self):
        df = self.df_delta[20:]
        delta = df['price']
        dates = map(lambda x: x[0], self.ratio_list)
        ratio = map(lambda x: x[1], self.ratio_list)

        fig = Figure(figsize=[12, 8])
        ax1 = fig.add_axes([.1, .1, .8, .8])
        ax2 = ax1.twinx()
        ax1.plot(dates, delta, 'r-', label='delta')
        ax2.plot(dates, ratio, 'b-', label='ratio')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper center')
        canvas = FigureCanvasAgg(fig)

        # write image data to a string buffer and get the PNG image bytes
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class Volatility(object):

    def __init__(self):
        pass

    def GET(self, symbol):
        return render.volatility(symbol)


class VolBase(object):

    CACHE_DATE = None
    CACHE_DIC = None

    def __init__(self):
        pass

    def init_data(self, symbol):
        # df_equity = EquityDAO().get_date_price_list(symbol)
        # price_list = df_equity['price'].to_list()
        # OptionCalculater().get_year_history_volatility(price_list)

        # get the equity records from 100 date ago.
        from_date_str = (datetime.date.today() - datetime.timedelta(100)).strftime('%Y-%m-%d')
        equity_records = YahooEquityDAO().get_all_equity_price_by_symbol(symbol, from_date_str)
        current_quity_price = equity_records[-1][1]
        option_iv_records = OptionDAO().get_corresponding_implied_volatilities(symbol, current_quity_price)
        first_tradetime = option_iv_records[0][0]
        circle = 30
        equity_start_date = first_tradetime - datetime.timedelta(circle)
        trade_day_circle = len(filter(lambda x: x[0] >= equity_start_date and x[0] < first_tradetime, equity_records))
        hv_records = OptionCalculater.get_year_history_volatility_list(filter(lambda x: x[0] >= equity_start_date, equity_records), trade_day_circle)
        self.equity_records = filter(lambda x: x[0] >= first_tradetime, equity_records)
        self.hv_records = hv_records
        self.iv_records = option_iv_records
        if symbol.upper() == 'SPY':
            df = VIXDAO().get_vix_price_by_symbol('VIY00')
            self.iv_records = df.values.tolist()

    def init_with_cache(self, symbol):
        symbol = symbol.upper()
        if datetime.date.today() != VolBase.CACHE_DATE:
            VolBase.CACHE_DIC = {}
            VolBase.CACHE_DATE = datetime.date.today()
        if VolBase.CACHE_DIC.has_key(symbol):
            (self.equity_records, self.hv_records, self.iv_records) = VolBase.CACHE_DIC[symbol]
        else:
            self.init_data(symbol)
            VolBase.CACHE_DIC[symbol] = (self.equity_records, self.hv_records, self.iv_records)


class VolHvsI(VolBase):

    def GET(self, symbol):
        self.init_with_cache(symbol)
        dates = map(lambda x: x[0], self.equity_records)
        hv = map(lambda x: x[1] * 100.0, self.hv_records)
        iv = map(lambda x: x[1], self.iv_records)
        fig = Figure(figsize=[12, 6])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, hv, label='historical volatility')
        ax.plot(dates, iv, label='implied volatility')
        ax.legend(loc='upper left')
        ax.grid()
        # conver to canvas
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class VolEquity(VolBase):

    def GET(self, symbol):
        self.init_with_cache(symbol)
        dates = map(lambda x: x[0], self.equity_records)
        equity_prices = map(lambda x: x[1], self.equity_records)
        fig = Figure(figsize=[12, 6])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, equity_prices, label='price')
        ax.legend(loc='upper left')
        ax.grid()

        #conver to canvas
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class FindOption(object):

    def __init__(self):
        pass

    #def GET(self):
    #    return render.findoption('SPY,QQQ', 'QQQ', [1, 2], '', [], '')

    def GET(self):
        query_string = web.ctx.query
        query_dic = parse_query_string(query_string)
        symbols = ETFS.get_option_symbols()
        option_dao = OptionDAO()
        selected_symbol = query_dic.get('symbol')
        if selected_symbol is None:
            selected_symbol = 'SPY'

        unexpriated_dates = option_dao.get_all_unexpired_dates(selected_symbol)
        expiration_dates = map(lambda x: x.strftime('%Y-%m-%d'), unexpriated_dates)
        selected_expiration_date = query_dic.get('expiration')
        if selected_expiration_date is None:
            for exp_date in unexpriated_dates:
                if exp_date.weekday() == 4 and 14 < exp_date.day < 22:
                    selected_expiration_date = exp_date.strftime('%Y-%m-%d')
                    break
        strike_prices = option_dao.get_strike_prices_by(selected_symbol, selected_expiration_date)
        selected_strike_price = query_dic.get('strike_price')
        if selected_strike_price is None:
            current_equity_price = EquityDAO().get_latest_price(selected_symbol)
            min = sys.maxint
            for strike_price in strike_prices:
                delta = abs(strike_price - current_equity_price)
                if delta < min:
                    min = delta
                    selected_strike_price = strike_price
        return render.findoption(','.join(symbols), selected_symbol, ','.join(expiration_dates), selected_expiration_date, ','.join(map(str, strike_prices)), selected_strike_price)


class Greeks(object):

    def __init__(self):
        pass

    def GET(self, symbol):
        records = OptionDAO().get_option_by_symbol(symbol)
        print records
        return render.greeks(symbol, records)




def run_web_app():
    urls = ('/', 'Index',
            '/credit', 'Credit',
            '/vix', 'VixAll',
            '/vixindex', 'VIXIndex',
            '/vixf1', 'VIXF1',
            '/vixf2', 'VIXF2',
            '/vix3in1', 'VIX3in1',
            '/spyvixhedge', 'SPYVIXHedge',
            '/volatility/(.*)', 'Volatility',
            '/volhvsi/(.*)', 'VolHvsI',
            '/volequity/(.*)', 'VolEquity',
            '/findoption', 'FindOption',
            '/greeks/(.*)', 'Greeks')

    app = web.application(urls, globals())
    app.run()

if __name__ == '__main__':
    pass
    # if the code run on linux server...
    #if platform.system() == 'Linux':
    #    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    #app.run()
    #print SPYVIXHedge().get_vix_delta()