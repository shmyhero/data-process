import web
import datetime
import cStringIO
import sys
import numpy as np
from matplotlib.dates import AutoDateLocator, DateFormatter
from utils.stringhelper import all_number_p
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from utils.querystringparser import parse_query_string
from utils.cachehelper import CacheMan
from utils.maths import half_adjust_round
from common.symbols import Symbols
from common.optioncalculater import OptionCalculater
from common.tradetime import TradeTime
from entities.vix import VIX
from dataaccess.basedao import BaseDAO
from dataaccess.equitydao import EquityDAO
from dataaccess.vixdao import VIXDAO
from dataaccess.nysecreditdao import NYSECreditDAO
from dataaccess.yahooequitydao import YahooEquityDAO
from dataaccess.optiondao import OptionDAO
from dataaccess.spyvixhedgedao import SPYVIXHedgeDAO
from dataaccess.optionskewdao import OptionSkewDAO
from dataaccess.processdao import ProcessDAO
from dataaccess.equityrealtimedao import EquityRealTimeDAO
from dataaccess.equitymindao import EquityMinDAO
from research.optionbacktest import OptionBackTest
from ingestion.yahooscraper import YahooScraper
from ingestion.cboescraper import CBOEScraper
from ingestion.marketwatchscraper import MarketWatchScraper


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
        #print credits_df
        #print spy_df
        credits_df = credits_df[credits_df.lastDate >= '2008-01-01']
        spy_df = spy_df[spy_df.lastdate >= datetime.date(2008, 1, 1)]
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
        ax1.grid()
        canvas = FigureCanvasAgg(fig)

        # write image data to a string buffer and get the PNG image bytes
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class VIXFutures(object):

    def __init__(self):
        pass

    def get_historical_volatility(self, new_price, from_date=None):
        if from_date is None:
            from_date = (datetime.date.today() - datetime.timedelta(150))
        else:
            from_date = from_date - datetime.timedelta(37) # ensure more than 21 days
        # equity_records = EquityDAO().get_all_equity_price_by_symbol('SPY', from_date)
        equity_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date.strftime('%Y-%m-%d'), 'Closeprice')
        if new_price is not None:
            equity_records.append([datetime.date.today(), new_price])
        hv_records = OptionCalculater.get_year_history_volatility_list(equity_records, 21)
        return hv_records

    def get_equity_prices(self, symbol, from_date, new_price):
        # equity_records = EquityDAO().get_all_equity_price_by_symbol(symbol, from_date)
        equity_records = YahooEquityDAO().get_all_equity_price_by_symbol('SPY', from_date.strftime('%Y-%m-%d'),'Closeprice')
        if new_price is not None:
            equity_records.append([datetime.date.today(), new_price])
        equity_prices = map(lambda x: x[1], equity_records)
        return equity_prices

    def get_low_and_upper(self, spy_values, vix_values):
        low_rate = 1.25 * np.sqrt(21)/100/np.sqrt(252)
        high_rate = 1.75 * np.sqrt(21)/100/np.sqrt(252)
        spy_low = map(lambda x, y: x * (1 + low_rate*y), spy_values, vix_values)
        spy_high = map(lambda x, y: x * (1 + high_rate*y), spy_values, vix_values)
        return [spy_low, spy_high]

    def shift_values(self, values):
        append_values = [values[-1]] * 21
        shifted_values = values[21:] + append_values
        return shifted_values

    def GET(self, from_date_str=None):
        default_from_date = TradeTime.get_latest_trade_date() - datetime.timedelta(60)
        if from_date_str is None or from_date_str == '':
            from_date = default_from_date
        else:
            try:
                input_from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
                from_date = TradeTime.get_from_date_by_window(22, input_from_date)
            except Exception:
                from_date = default_from_date
        # records_index = VIXDAO().get_vix_price_by_symbol_and_date('VIY00', from_date=from_date)
        records_index = YahooEquityDAO().get_all_equity_price_by_symbol('^VIX', from_date.strftime('%Y-%m-%d'),'Closeprice')
        (records_f1, records_f2, records_f3) = VIXDAO().get_following_vix(from_date)
        new_spy_price = None
        if datetime.date.today() > TradeTime.get_latest_trade_date():
            try:
                new_spy_price = YahooScraper.get_data_by_symbol('SPY')
            except Exception as e:
                new_spy_price = MarketWatchScraper.get_data_by_symbol('SPY')
            try:
                new_vix_price = YahooScraper.get_data_by_symbol('VIX')
            except Exception as e:
                new_vix_price = MarketWatchScraper.get_data_by_symbol('VIX')
            new_vix_features = CBOEScraper.get_vix_future()
            [new_f1, new_f2, new_f3] = [new_vix_features[0][2], new_vix_features[1][2], new_vix_features[2][2]]
            records_index.append([datetime.date.today(), new_vix_price])
            records_f1.append([datetime.date.today(), new_f1])
            records_f2.append([datetime.date.today(), new_f2])
            records_f3.append([datetime.date.today(), new_f3])
        dates = map(lambda x: x[0], records_index)
        price_index = map(lambda x: x[1], records_index)
        price_f1 = map(lambda x: x[1], records_f1)
        price_f2 = map(lambda x: x[1], records_f2)
        price_f3 = map(lambda x: x[1], records_f3)
        hv_records = self.get_historical_volatility(new_spy_price, from_date)[-len(dates):]
        hv_prices = map(lambda x: x[1]*100, hv_records)
        spy_prices = self.get_equity_prices('SPY', from_date, new_spy_price)
        [spy_low, spy_high] = self.get_low_and_upper(spy_prices, price_index)

        # shift
        append_dates = TradeTime.generate_dates(dates[-1], dates[-1] + datetime.timedelta(days=50))

        dates = dates[21:] + (append_dates[0:21])
        hv_prices = self.shift_values(hv_prices)
        spy_prices = self.shift_values(spy_prices)
        price_index = self.shift_values(price_index)
        price_f1 = self.shift_values(price_f1)
        price_f2 = self.shift_values(price_f2)
        price_f3 = self.shift_values(price_f3)

        if from_date < default_from_date:
            dates = dates[:42]
            hv_prices = hv_prices[:42]
            spy_prices = spy_prices[:42]
            spy_low = spy_low[:42]
            price_index = price_index[:42]
            price_f1 = price_f1[:42]
            price_f2 = price_f2[:42]
            price_f3 = price_f3[:42]


        fig = Figure(figsize=[24, 8])
        ax1 = fig.add_axes([.1, .1, .8, .8])
        ax2 = ax1.twinx()
        ax1.plot(dates, hv_prices, label='historical volatility', color='black')
        ax1.plot(dates, price_index, label='vix index', color='blue')
        ax1.plot(dates, price_f1, label='vix first month', color='deepskyblue')
        ax1.plot(dates, price_f2, label='vix second month', color='lightskyblue')
        ax1.plot(dates, price_f3, label='vix third month', color='lightblue')
        ax1.legend(loc='upper left')

        ax2.plot(dates, spy_prices, 'red', label='SPY')
        ax2.plot(dates, spy_low, 'orange', label='spy_low')
        # ax2.plot(dates, spy_high, 'yellow', label='spy_high')
        ax2.legend(loc='upper right')
        ax1.grid()
        ax1.xaxis.set_major_formatter(DateFormatter('%y%m%d'))
        ax1.set_xticks(dates)
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class SVXYForVIX(object):

    def GET(self, from_date_str=None):
        default_from_date = TradeTime.get_latest_trade_date() - datetime.timedelta(60)
        if from_date_str is None or from_date_str == '':
            from_date = default_from_date
        else:
            try:
                input_from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
                from_date = TradeTime.get_from_date_by_window(22, input_from_date)
            except Exception:
                from_date = default_from_date
        records_svxy = YahooEquityDAO().get_all_equity_price_by_symbol('SVXY', from_date.strftime('%Y-%m-%d'), 'Closeprice')
        dates = map(lambda x: x[0], records_svxy)
        price_svxy = map(lambda x: x[1], records_svxy)

        # shift
        append_dates = TradeTime.generate_dates(dates[-1], dates[-1] + datetime.timedelta(days=50))
        dates = dates[21:] + append_dates[1:22]
        price_svxy = price_svxy[21:] + [price_svxy[-1]] * 21

        if from_date < default_from_date:
            dates = dates[:42]
            price_svxy = price_svxy[:42]

        fig = Figure(figsize=[24, 8])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, price_svxy, label='SVXY')
        ax.legend(loc='upper left')
        ax.grid()
        ax.xaxis.set_major_formatter(DateFormatter('%y%m%d'))
        ax.set_xticks(dates)
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class EquityPrices(object):

    def GET(self, symbol, days):
        try:
            days = int(days)
        except Exception:
            days = 63
        from_date = TradeTime.get_latest_trade_date() - datetime.timedelta(days)
        equity_records = EquityDAO().get_all_equity_price_by_symbol(symbol, from_date)
        if datetime.date.today() > TradeTime.get_latest_trade_date():
            new_spy_price = YahooScraper.get_data_by_symbol(symbol)
            equity_records.append([datetime.date.today(), new_spy_price])
        dates = map(lambda x: x[0], equity_records)
        equity_prices = map(lambda x: x[1], equity_records)
        fig = Figure(figsize=[16, 4])
        ax = fig.add_axes([.1, .1, .8, .9])
        ax.plot(dates, equity_prices, label='price')
        ax.legend(loc='upper left')
        ax.grid()
        ax.xaxis.set_major_formatter(DateFormatter('%y%m%d'))
        ax.set_xticks(dates)
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)

        # conver to canvas
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class VIX3in1(object):

    def GET(self):
        from_date = TradeTime.get_latest_trade_date() - datetime.timedelta(30)
        vix_records = VIXDAO().get_vix_price_by_symbol_and_date('VIY00', from_date=from_date)
        dates = map(lambda x: x[0], vix_records)
        vix_prices = map(lambda x: x[1], vix_records)
        vxv_records = YahooEquityDAO().get_all_equity_price_by_symbol('^VXV', from_date_str=from_date.strftime('%Y-%m-%d'))
        vxmt_records = YahooEquityDAO().get_all_equity_price_by_symbol('^VXMT', from_date_str=from_date.strftime('%Y-%m-%d'))
        vxv_prices = map(lambda x: x[1], vxv_records)
        vxmt_prices = map(lambda x: x[1], vxmt_records)
        fig = Figure(figsize=[12, 8])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, vix_prices, label='vix')
        ax.plot(dates, vxv_prices, label='vxv')
        ax.plot(dates, vxmt_prices, label='vxmt')
        ax.legend(loc='upper left')
        ax.grid()
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class VIX(object):

    def GET(self):
        return render.vix()


class SPYVIXHedge(object):

    def __init__(self):
        pass

    def get_report(self):
        records = SPYVIXHedgeDAO().select_all()
        for record in records:
            date = record[1]
            result = [date]
            fixed_values = map(lambda x: half_adjust_round(x, 2), record[2:])
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

        # get the equity records from 150 date ago.
        #from_date_str = (datetime.date.today() - datetime.timedelta(150)).strftime('%Y-%m-%d')
        from_date = (datetime.date.today() - datetime.timedelta(150))
        #equity_records = YahooEquityDAO().get_all_equity_price_by_symbol(symbol, from_date_str)
        equity_records = EquityDAO().get_all_equity_price_by_symbol(symbol, from_date)
        current_quity_price = equity_records[-1][1]
        option_iv_records = OptionDAO().get_corresponding_implied_volatilities(symbol, current_quity_price)
        first_tradetime = option_iv_records[0][0]
        circle = 30
        equity_start_date = first_tradetime - datetime.timedelta(circle)
        # trade_day_circle = len(filter(lambda x: x[0] >= equity_start_date and x[0] < first_tradetime, equity_records))
        hv_records = OptionCalculater.get_year_history_volatility_list(filter(lambda x: x[0] >= equity_start_date, equity_records), circle)
        self.equity_records = filter(lambda x: x[0] >= first_tradetime, equity_records)
        self.hv_records = hv_records
        self.iv_records = option_iv_records
        if symbol.upper() == 'SPY':
            self.iv_records = VIXDAO().get_vix_price_by_symbol('VIY00')

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
        if all_number_p(symbol):
            self.init_data(symbol)
        else:
            self.init_with_cache(symbol)
        dates = map(lambda x: x[0], self.hv_records)
        hv = map(lambda x: x[1] * 100.0, self.hv_records)
        if all_number_p(symbol):
            iv = map(lambda x: x[1] * 100.0, self.iv_records[-len(dates):])
        else:
            iv = map(lambda x: x[1], self.iv_records[-len(dates):])
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


class OptionVolSkew(object):

    def GET(self, symbol):
        df = OptionSkewDAO().select_by_symbol(symbol)
        dates = df['tradeTime'].get_values()
        skews = df['skew'].get_values()
        fig = Figure(figsize=[12, 6])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, skews, label='option volatility skew')
        ax.legend(loc='upper left')
        ax.grid()

        # conver to canvas
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


class FindOption(object):

    def __init__(self):
        query_string = web.ctx.query
        self.query_dic = parse_query_string(query_string)

    def get_symbols(self):
        symbols =  Symbols.get_option_symbols()
        symbols.append('^VIX')
        symbols.append('510050')
        return symbols

    def get_selected_symbol(self):
        selected_symbol = self.query_dic.get('symbol')
        if selected_symbol is None:
            selected_symbol = 'SPY'
        return selected_symbol

    def get_unexpired_dates(self, selected_symbol, delta_days = 60):
        unexpired_dates = OptionDAO().get_all_unexpired_dates(selected_symbol, from_date=TradeTime.get_latest_trade_date() - datetime.timedelta(days=delta_days))
        return unexpired_dates

    def get_selected_expiration_date(self, unexpired_dates):
        selected_expiration_date = self.query_dic.get('expiration')
        if selected_expiration_date is None:
            filtered_dates = filter(lambda x: x > TradeTime.get_latest_trade_date(), unexpired_dates)
            for exp_date in filtered_dates:
                if exp_date.weekday() == 4 and 14 < exp_date.day < 22:
                    return exp_date.strftime('%Y-%m-%d')
            # if not find, return the first element of filtered dates,
            # e.g. ^VIX is a special option, the expiration date is not the third Friday likes other option...
            if len(filtered_dates) > 0:
                return filtered_dates[0].strftime('%Y-%m-%d')
        else:
            return selected_expiration_date

    def get_strike_prices(self, selected_symbol, selected_expiration_date):
        strike_prices = OptionDAO().get_strike_prices_by(selected_symbol, selected_expiration_date)
        return strike_prices

    def get_selected_strike_price(self, selected_symbol, strike_prices):
        selected_strike_price = self.query_dic.get('strike_price')
        if selected_strike_price is None:
            if selected_symbol == '^VIX':
                current_equity_price = YahooEquityDAO().get_latest_price(selected_symbol)
            else:
                current_equity_price = EquityDAO().get_latest_price(selected_symbol)
            min_delta = sys.maxint
            for strike_price in strike_prices:
                delta = abs(strike_price - current_equity_price)
                if delta < min_delta:
                    min_delta = delta
                    selected_strike_price = strike_price
        return selected_strike_price

    def get_all_parameters(self):
        symbols = self.get_symbols()
        selected_symbol = self.get_selected_symbol()
        unexpired_dates = self.get_unexpired_dates(selected_symbol)
        expiration_dates = map(str, unexpired_dates)
        selected_expiration_date = self.get_selected_expiration_date(unexpired_dates)
        strike_prices = self.get_strike_prices(selected_symbol, selected_expiration_date)
        selected_strike_price = self.get_selected_strike_price(selected_symbol, strike_prices)
        return [','.join(symbols), selected_symbol, ','.join(expiration_dates), selected_expiration_date, ','.join(map(str, strike_prices)), selected_strike_price]


class OptionForGreeks(FindOption):

    def __init__(self):
        FindOption.__init__(self)

    #def GET(self):
    #    return render.findoption('SPY,QQQ', 'QQQ', [1, 2], '', [], '')

    def GET(self):
        parameters = self.get_all_parameters()
        return render.option_for_greeks(*parameters)


class OptionsForBackTest(FindOption):

    def __init__(self):
        FindOption.__init__(self)

    def get_unexpired_dates(self, selected_symbol, delta_days = 10000):
        return super(OptionsForBackTest, self).get_unexpired_dates(selected_symbol, delta_days)

    def GET(self):
        parameters = self.get_all_parameters()
        parameters.append(self.query_dic.get('option_quantity_list'))
        return render.options_for_back_test(*parameters)


class Greeks(object):

    def __init__(self):
        pass

    def fix_for_record(self, record):
        new_record = list(record)
        for i in range(5):
            if new_record[2+i] is not None:
                new_record[2 + i] = half_adjust_round(record[2 + i], 3)
        return new_record

    def GET(self, symbol):
        records = CacheMan('greeks').get_with_cache(symbol, OptionDAO().compatible_get_option_by_symbol)
        new_records = map(self.fix_for_record, records[-20:])
        return render.greeks(symbol, new_records)


class GreeksDiagram(object):

    def __init__(self):
        pass

    def plot(self, date_value_list, label):
        dates = map(lambda x: x[0], date_value_list)
        values = map(lambda x: x[1], date_value_list)
        fig = Figure(figsize=[12, 3])
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
        records = CacheMan('portal_greeks').get_with_cache(symbol, OptionDAO().compatible_get_option_by_symbol)
        field_index_dic = {'lastprice':1, 'delta':2, 'gamma':3, 'vega':4, 'theta':5, 'volatility':6}
        index = field_index_dic[field.lower()]
        if index is not None:
            date_value_list = map(lambda x: [x[0], x[index]], records[-20:])
            return self.plot(date_value_list, field)
        return None


class OptionBackTestDiagram(object):

    def __init__(self):
        query_string = web.ctx.query
        self.query_dic = parse_query_string(query_string)
        self.option_quantity_query = self.query_dic.get('option_quantity_list')
        self.option_quantity_list = OptionBackTestDiagram.parse_option_quantity(self.option_quantity_query)
        self.start_date = datetime.datetime.strptime(self.query_dic.get('start_date'), '%Y-%m-%d').date()

    @staticmethod
    def parse_option_quantity(query_str):
        result = []
        for record_str in query_str.split(';'):
            record = record_str.split(',')
            option_symbol = record[0]
            quantity = int(record[1])
            long_short = record[2]
            result.append([option_symbol, quantity, long_short])
        return result

    def plot(self, date_value_list, label):
        dates = map(lambda x: x[0], date_value_list)
        values = map(lambda x: x[1], date_value_list)
        fig = Figure(figsize=[12, 8])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(dates, values, label=label)
        ax.legend(loc='upper left')
        ax.grid()

        # convert to canvas
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data

    def GET(self):
        date_values = OptionBackTest(self.option_quantity_list, self.start_date).get_values()
        return self.plot(date_values, self.option_quantity_query)


class ProcessStatus(object):

    def __init__(self):
        pass

    @staticmethod
    def get_display_records(processes_info):
        records = []
        for process_info in processes_info:
            record = process_info
            if process_info[1] is True:
                record[1] = 'Completed'
                record.append('lightgreen')
            elif process_info[2] is not None:
                if process_info[3] is None:
                    record[1] = 'Running'
                    record.append('khaki')
                else:
                    record[1] = 'Failed'
                    record.append('tomato')
            else:
                record[1] = 'Not Started'
                record.append('white')
            records.append(record)
        return records

    def GET(self):
        # yahoo_equity_processes_info = ProcessDAO().get_latest_processes('yahoo-equity-process')
        # yahoo_equity_records = ProcessStatus.get_display_records(yahoo_equity_processes_info)
        # barchart_option_processes_info = ProcessDAO().get_latest_processes('barchart-option-process')
        # barchart_option_records = ProcessStatus.get_display_records(barchart_option_processes_info)
        # return render.process_status(yahoo_equity_records, barchart_option_records)
        data_processes_info = ProcessDAO().get_latest_processes('data-process')
        records = ProcessStatus.get_display_records(data_processes_info)
        return render.process_status(records)


class Others(object):

    def __init__(self):
        pass

    def GET(self):
        return render.others()


class StartEndDate(object):

    def __init__(self):
        pass

    def GET(self):
        records = YahooEquityDAO().get_start_end_date_by_symbols()
        last_trade_date = TradeTime.get_latest_trade_date()
        error = False
        for record in records:
            if record[2] < last_trade_date:
                error = True
        dic = Symbols.get_yahoo_mapping_dic()
        return render.start_end_date(records, last_trade_date, error, dic)


class RealTimeDataStatus(object):

    def __init__(self):
        pass

    def GET(self):
        svxy_integrity_p, svxy_results = EquityRealTimeDAO().validate_integrity_for_real_time_data('SVXY')
        spy_integrity_p, spy_results = EquityRealTimeDAO().validate_integrity_for_real_time_data('SPY')
        return render.realtime_data_status(svxy_integrity_p, svxy_results, spy_integrity_p, spy_results)


class MinDataStatus(object):

    def __init__(self):
        pass

    def GET(self):
        symbols = ['SPX', 'VIX', 'SVXY', 'UVXY', 'SPY', 'QQQ', 'QLD', 'SSO', 'TLT', 'UBT']
        dao = EquityMinDAO()
        status_list = map(lambda x: [x, dao.validate_integrity_for_min_data(x)], symbols)
        return render.min_data_status(status_list)


class UpperSPY(object):

    def __init__(self):
        from_date = (datetime.date.today() - datetime.timedelta(150))
        self.spy_records = EquityDAO().get_all_equity_price_by_symbol('SPY', from_date)
        self.vix_records = VIXDAO().get_vix_price_by_symbol_and_date('VIY00', from_date=from_date)
        if datetime.date.today() > TradeTime.get_latest_trade_date():
            new_spy_price = YahooScraper.get_data_by_symbol('SPY')
            new_vix_price = YahooScraper.get_data_by_symbol('VIX')
            self.spy_records.append([datetime.date.today(), new_spy_price])
            self.vix_records.append([datetime.date.today(), new_vix_price])
        self.dates = map(lambda x: x[0], self.spy_records)
        self.spy_values = map(lambda x: x[1], self.spy_records)
        self.vix_values = map(lambda x: x[1], self.vix_records)

    def GET(self):
        low_rate = 1.25 * np.sqrt(21)/100/np.sqrt(252)
        high_rate = 1.75 * np.sqrt(21)/100/np.sqrt(252)
        spy_low = map(lambda x, y: x * (1 + low_rate*y), self.spy_values, self.vix_values)
        spy_high = map(lambda x, y: x * (1 + high_rate*y), self.spy_values, self.vix_values)
        append_dates = TradeTime.generate_dates(self.dates[-1], self.dates[-1] + datetime.timedelta(days=50))
        shifted_dates = self.dates[21:] + (append_dates[0:21])
        append_spy_values = [self.spy_values[-1]] * 21
        shifted_spy_values = self.spy_values[21:] + append_spy_values
        fig = Figure(figsize=[60, 10])
        ax = fig.add_axes([.1, .1, .8, .8])
        ax.plot(shifted_dates, shifted_spy_values, label='spy', color='black')
        ax.plot(shifted_dates, spy_low, label='spy low', color='blue')
        # line1.set_dashes([2, 4])
        ax.plot(shifted_dates, spy_high, label='spy high', color='skyblue')
        # line2.set_dashes([8, 4, 2, 4, 2, 4])
        # autodates = AutoDateLocator()
        # ax.xaxis.set_major_locator(autodates)
        yearsFmt = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.set_xticks(shifted_dates)

        # ax.xticks(shifted_dates, rotation=90)
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.legend(loc='upper left')
        ax.grid()
        canvas = FigureCanvasAgg(fig)
        buf = cStringIO.StringIO()
        canvas.print_png(buf)
        data = buf.getvalue()
        return data


def run_web_app():
    urls = ('/', 'Index',
            '/credit', 'Credit',
            '/vixfutures/(.*)', 'VIXFutures',
            '/svxyforvix/(.*)', 'SVXYForVIX',
            '/equityprices/(.*)/(.*)', 'EquityPrices',
            '/vix3in1', 'VIX3in1',
            '/vix', 'VIX',
            '/spyvixhedge', 'SPYVIXHedge',
            '/volatility/(.*)', 'Volatility',
            '/volhvsi/(.*)', 'VolHvsI',
            '/volequity/(.*)', 'VolEquity',
            '/optionvolskew/(.*)', 'OptionVolSkew',
            '/optionforgreeks', 'OptionForGreeks',
            '/greeks/(.*)', 'Greeks',
            '/greeksdiagram/(.*)/(.*)', 'GreeksDiagram',
            '/optionsforbacktest', 'OptionsForBackTest',
            '/optionbacktest', 'OptionBackTestDiagram',
            '/processstatus', 'ProcessStatus',
            '/startenddate', 'StartEndDate',
            '/realtimedatastatus', 'RealTimeDataStatus',
            '/mindatastatus', 'MinDataStatus',
            '/upperspy', 'UpperSPY',
            '/others', 'Others')

    app = web.application(urls, globals())
    app.run()

if __name__ == '__main__':
    pass
    # if the code run on linux server...
    #if platform.system() == 'Linux':
    #    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    #app.run()
    #print SPYVIXHedge().get_vix_delta()