import web
import datetime
import cStringIO
import sys
from decimal import Decimal
from abc import abstractmethod
from utils.querystringparser import parse_query_string
from utils.cachehelper import CacheMan
from common.etfs import ETFS
from common.optioncalculater import OptionCalculater
from entities.vix import VIX
from dataaccess.basedao import BaseDAO
from dataaccess.equitydao import EquityDAO
from dataaccess.vixdao import VIXDAO
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.optiondao import OptionDAO
from dataaccess.spyvixhedgedao import SPYVIXHedgeDAO
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
        pass

    def round2(self, num):
        return float('{:.2f}'.format(Decimal(num)))


    def get_report(self):
        records = SPYVIXHedgeDAO().select_all()
        for record in records:
            date = record[1]
            result = [date]
            fixed_values = map(self.round2, record[2:])
            result.extend(fixed_values)
            yield result

    def GET(self):
        report_data = list(self.get_report())
        return render.spyvixhedge(report_data)


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

    # can be refactor to use cache man.
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
        records = CacheMan('greeks').get_with_cache(symbol, OptionDAO().get_option_by_symbol)
        return render.greeks(symbol, records)


class GreeksDiagram(object):

    def __init__(self):
        pass

    def plot(self, date_value_list, label):
        dates = map(lambda x: x[0], date_value_list)
        values = map(lambda x: x[1], date_value_list)
        fig = Figure(figsize=[12, 6])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, values, label=label)
        ax.legend(loc='upper left')
        ax.grid()

        # conver to canvas
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data

    def GET(self, symbol, field):
        records = CacheMan('portal_greeks').get_with_cache(symbol, OptionDAO().get_option_by_symbol)
        field_index_dic = {'lastprice':1, 'delta':2, 'gamma':3, 'vega':4, 'theta':5}
        index = field_index_dic[field.lower()]
        if index is not None:
            date_value_list = map(lambda x: [x[0], x[index]], records[-20:])
            return self.plot(date_value_list, field)
        return None



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
            '/greeks/(.*)', 'Greeks',
            '/greeksdiagram/(.*)/(.*)', 'GreeksDiagram')

    app = web.application(urls, globals())
    app.run()

if __name__ == '__main__':
    pass
    # if the code run on linux server...
    #if platform.system() == 'Linux':
    #    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    #app.run()
    #print SPYVIXHedge().get_vix_delta()