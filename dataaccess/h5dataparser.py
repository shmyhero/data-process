#ETF_VIXFutures_data_05-17-17.h5
import pandas as pd
from datetime import datetime
from utils.stringhelper import string_fetch
from entities.equity import Equity
from entities.option import Option
from entities.vix import VIX
from common.etfs import ETFS


class H5DataOptionParser(object):

    def __init__(self, option_data_file):
        self.option_data_file = option_data_file
        self.trade_date = self.get_trade_date()
        self.equity_records = []
        self.option_records = []


    def get_trade_date(self):
        date_str = string_fetch(self.option_data_file, '_data_', '.h5')
        # print date_str
        trade_date = datetime.strptime(date_str, '%m-%d-%y')
        return trade_date

    def parse_option_data_by_symbol(self, symbol):
        df = pd.read_hdf(self.option_data_file, symbol)
        if df is not None:
            print '{} data exists, parse it to object...'.format(symbol)
            equity = Equity()
            equity.symbol = symbol
            equity.tradeTime = self.trade_date
            self.equity_records.append(equity)
            for index, row in df.iterrows():
                equity.lastPrice = row['Underlying_Price']
                option = Option()
                option.symbol = symbol
                option.tradeTime = self.trade_date,
                option.expirationDate = row['Expiry']
                option.optionType = row['Type']
                option.strikePrice = row['Strike']
                option.bidPrice = row['Bid']
                option.lastPrice = row['Last']
                option.priceChange = row['Change']
                option.volatility = row['ImpliedVolatility']
                option.theoretical = row['TheoreticalValue']
                option.delta = row['Delta']
                option.gamma = row['Gamma']
                option.rho = row['Rho']
                option.theta = row['Theta']
                option.vega = row['Vega']
                option.openInterest = row['Open Int']
                option.volume = row['Volume']
                self.option_records.append(option)
        else:
            print 'Missing data for {} ...'.format(symbol)

    def load_all(self):
        for symbol in ETFS.get_all_symbols():
            self.parse_option_data_by_symbol(symbol)


class H5DataVixParser(object):

    def __init__(self, vix_data_file):
        self.vix_data_file = vix_data_file
        self.vix_records = []

    def parse_vix_data(self):
        df = pd.read_hdf(self.vix_data_file, 'VIX')
        vix = VIX()
        for index, row in df.iterrows():
            vix.symbol = index
            vix.lastPrice = row['lastPrice']
            vix.priceChange = row['priceChange']
            vix.openPrice = row['openPrice']
            vix.highPrice = row['highPrice']
            vix.lowPrice = row['lowPrice']
            vix.previousPrice = row['previousPrice']
            vix.volume = row['volume']
            vix.tradeTime = row['tradeTime']
            vix.dailyLastPrice = row['dailyLastPrice']
            vix.dailyPriceChange = row['dailyPriceChange']
            vix.dailyOpenPrice = row['dailyOpenPrice']
            vix.dailyHighPrice = row['dailyHighPrice']
            vix.dailyLowPrice = row['dailyLowPrice']
            vix.dailyPreviousPrice = row['dailyPreviousPrice']
            vix.dailyVolume = row['dailyVolume']
            vix.dailyDate1dAgo = row['dailyDate1dAgo']
            self.vix_records.append(vix)

if __name__ == '__main__':
    option_parser = H5DataOptionParser('/Users/tradehero/python-projects/stock-data/Barchart_Options_Data/ETF_options_data_04-20-17.h5')
    option_parser.load_all()
    print option_parser.equity_records

    vix_parser = H5DataVixParser('/Users/tradehero/python-projects/stock-data/Barchart_VIXFutures_Data/ETF_VIXFutures_data_07-16-17.h5')
    vix_parser.parse_vix_data()
    print len(ETFS.get_all_symbols())
    #print vix_parser.vix_records







