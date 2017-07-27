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

    def export_data_to_csv(self, path):
        self.select_all().to_csv(path)


if __name__ == '__main__':
    #print OptionSkew().select_all()
    #print OptionSkew().select_by_symbol('SPY')
    OptionSkewDAO().export_data_to_csv('/Users/tradehero/skew.csv')