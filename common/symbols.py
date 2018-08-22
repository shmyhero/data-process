from utils.listhelper import flatten
from utils.listhelper import hash_to_list, list_to_hash


class Symbols(object):

    dic = {
       'Large Cap'             :['SPY','IVV','VOO','IWB'],
       'Mid Cap'               :['MDY','IJH','VO','IWR'],
       'Small Cap'             :['IWM','IJR','VB'],
       'Global Equity'         :['VEU','ACWI','VXUS'],
       'AsiaPac Equity'        :['EWT','EWY','EWA','EWS','AAXJ','FXI','EWH','EWM','EPI','INDA','RSX'],
       'Europe Equity'         :['FEZ','EZU','VGK','HEDJ','EWU','EWI','EWP','EWQ','EWL','EWD'],
       'Emerging | Frontier'   :['EWZ','EWW','ECH','FM','EEM','VWO'],
       'Real Estate'           :['RWO','RWX','RWR','IYR','VNQ'],
       'Consumer Discretionary':['XLY','XRT','FXD','VCR','RTH'],
       'Consumer Staples'      :['XLP','FXG','VDC','ECON'],
       'Energy'                :['XLE','XOP','VDE','IYE','IXC','OIH'],
       'Financials'            :['XLF','KBE','KIE','IYG','KRE'],
       'Healthcare'            :['XLV','XBI','IBB'],
       'Industrial'            :['XLI','IYT','VIS','IYJ'],
       'Materials'             :['XLB','XHB','XME','IGE','MOO','LIT'],
       'Technology'            :['XLK','SMH','HACK','FDN', 'QQQ'],
       'Telecom'               :['IYZ','IXP','VOX'],
       'Utilities'             :['IDU','XLU','VPU'],
       'Oil | Gas'             :['UNG','BNO'],
       'Precious Metals'       :['GLD','SLV','IAU'],
       'Bonds'                 :['BND','AGG','JNK','LQD'],
       'T-Bond'                :['TLT','IEF','IEI','SHY'],
       'Precious Metals Miners':['SIL','GDX','GDXJ'],
       'Volatility'            :['VXX', 'VXZ', 'UVXY','SVXY'], #, 'XIV', 'ZIV'] # no options for XIV and ZIV
       'Others'                :['DIA', 'EFA', 'EWJ', 'SSO', 'QLD', 'TQQQ', 'TLH', 'HYG', 'UBT', 'TMF', 'VWO', 'GSG'],
       'Stocks'                :['LMT', 'MO', 'CME', 'MA', 'V', 'AAPL']
        }

    non_option_symbols = ['ZIV', 'EDV', 'BRK-B', 'RHS', 'BIL', 'VNM', 'ITA', 'XAR', 'FNDE', 'DGRW', 'IHI', 'BJK', 'VHT', 'STZ','OIL', 'ADBE', 'AVGO', 'AMZN', 'NFLX', 'GOOG', 'AIEQ']

    indexes = ['^DJI', '^GSPC', '^VIX', '^VXV', '^VVIX', '^RUT', '^NDX']

    @staticmethod
    def get_option_symbols():
        return sorted(flatten(Symbols.dic.values()))

    @staticmethod
    def get_all_symbols():
        symbols = Symbols.get_option_symbols()
        symbols.extend(Symbols.non_option_symbols)
        symbols.extend(Symbols.indexes)
        return sorted(symbols)

    YahooSymbolMapping = {'SPX': '^GSPC', 'INDU': '^DJI', 'VIX': '^VIX', 'VXV': '^VXV', 'VVIX': '^VVIX', 'RUT': '^RUT', 'NDX': '^NDX', }

    @staticmethod
    def get_mapped_symbol(symbol, mapping_dic = YahooSymbolMapping):
        if symbol in mapping_dic.keys():
            return mapping_dic[symbol]
        else:
            return symbol

    @staticmethod
    def get_yahoo_mapping_dic():
        dic = {}
        reversed_mapping = Symbols.get_reversed_yahoo_symbol_mapping()
        for symbol in Symbols.get_all_symbols():
            if symbol[0] == '^':
                dic[reversed_mapping[symbol]] = symbol
            else:
                dic[symbol] = symbol
        return dic

    @staticmethod
    def get_reversed_yahoo_symbol_mapping():
        lst = hash_to_list(Symbols.YahooSymbolMapping)
        reversed_lst = map(lambda x: [x[1], x[0]], lst)
        dic = list_to_hash(reversed_lst)
        return dic

if __name__ == '__main__':
    # Symbols.yahoo_symbol_to_quantopian_symbol('^GSPC')
    print Symbols.get_yahoo_mapping_dic()
    # print Symbols.get_reversed_yahoo_symbol_mapping()



