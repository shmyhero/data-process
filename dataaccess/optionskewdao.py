import pandas as pd
from dataaccess.basedao import BaseDAO


class OptionSkewDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def select_all(self):
        columns = ['symbol', 'tradeTime', 'price', 'skew']
        query_template = """select {} from option_enough_liquidity_skew_view"""
        query = query_template.format(', '.join(columns))
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df

    def select_by_symbol(self, symbol):
        columns = ['symbol', 'tradeTime', 'price', 'skew']
        query_template = """select {} from option_enough_liquidity_skew_view where symbol = '{}'"""
        query = query_template.format(', '.join(columns), symbol)
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df

    def get_sorted_symbol_by_skew(self, date):
        query_template = """select symbol from option_enough_liquidity_skew_view where tradeTime = str_to_date('{}', '%Y-%m-%d') order by skew"""
        query = query_template.format(date)
        rows = self.select(query)
        ordered_symbols = map(lambda x: x[0], rows)
        return ordered_symbols

    def export_data_to_csv(self, path):
        self.select_all().to_csv(path)


if __name__ == '__main__':
    #print OptionSkew().select_all()
    #print OptionSkew().select_by_symbol('SPY')
    OptionSkewDAO().export_data_to_csv('/Users/tradehero/skew.csv')
    #sorted_symbols = OptionSkewDAO().get_sorted_symbol_by_skew('2017-07-24')
    #df_skew = pd.DataFrame(sorted_symbols)
    #df_skew.columns = ['symbol']
    #print df_skew
    #from dataaccess.equitydao import EquityDAO
    #df_price = EquityDAO().get_price_change_percentage('2017-07-24', '2017-07-26')
    #print df_price
    #newpd = pd.merge(df_skew, df_price, on='symbol')
    #print newpd