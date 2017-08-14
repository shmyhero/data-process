import web
import datetime
import platform
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahooequitydao import YahooEquityDAO
import cStringIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

#urls = ("/.*", "credit")
#urls = ("/", "Index",
#        "/credit", "Credit")


render = web.template.render('portal/templates')
#app = web.application(urls, globals())

class Index:

    def GET(self):
        #return """<a href=\"credit\">credit</a>"""
        return render.index()


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



if __name__ == "__main__":
    pass
    # if the code run on linux server...
    #if platform.system() == 'Linux':
    #    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    #app.run()