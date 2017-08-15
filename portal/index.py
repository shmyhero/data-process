import web
import datetime
import cStringIO
from abc import abstractmethod
from dataaccess.vixdao import VIXDAO
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahooequitydao import YahooEquityDAO
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
        from entities.vix import VIX
        symbols = VIX.get_following_symbols(datetime.datetime.now().strftime('%Y-%m-%d'))
        return list(symbols)[1]

    def get_label(self):
        return 'VIX First Month'

    def GET(self):
        return self.get_plot_data()


class VIXF2(VIXBase):

    def __init__(self):
        VIXBase.__init__(self)

    def get_symbol(self):
        from entities.vix import VIX
        symbols = VIX.get_following_symbols(datetime.datetime.now().strftime('%Y-%m-%d'))
        return list(symbols)[2]

    def get_label(self):
        return 'VIX Second Month'

    def GET(self):
        return self.get_plot_data()


def run_web_app():
    urls = ('/', 'Index',
            '/credit', 'Credit',
            '/vix', 'VixAll',
            '/vixindex', 'VIXIndex',
            '/vixf1', 'VIXF1',
            '/vixf2', 'VIXF2')

    app = web.application(urls, globals())
    app.run()

if __name__ == '__main__':
    pass
    # if the code run on linux server...
    #if platform.system() == 'Linux':
    #    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    #app.run()