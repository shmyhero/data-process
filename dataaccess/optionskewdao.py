import pandas as pd
from dataaccess.basedao import BaseDAO
from common.symbols import Symbols


class OptionSkewDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def get_all_skew_daily(self):
        columns = ['symbol', 'tradeTime', 'price', 'skew']
        query_template = """select {} from option_enough_liquidity_skew_view"""
        query = query_template.format(', '.join(columns))
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df

    def get_all_skew_weekly(self):
        columns = ['symbol', 'skew', 'balance_date']
        query_template = """select {} from option_skew_weekly_view"""
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

    def get_sorted_weekly_skew(self):
        df = self.get_all_skew_weekly()
        for name, group in df.groupby(df['balance_date']):
            group = group.sort_values('skew')
            symbol_list = group['symbol'].tolist()
            symbols = '_'.join(symbol_list)
            record = [name.strftime('%Y-%m-%d'), symbols]
            yield record

    def export_data_to_csv(self, file_path):
        records = list(self.get_sorted_weekly_skew())
        lines = map(lambda x: ','.join(x), records)
        schema = 'date,symbols'
        f = open(file_path, 'w')
        f.write(schema)
        f.write('\r\n')
        for line in lines:
            f.write(line)
            f.write('\r\n')
        f.close()


if __name__ == '__main__':
    #print OptionSkew().select_all()
    #print OptionSkew().select_by_symbol('SPY')
    OptionSkewDAO().export_data_to_csv('/Users/tradehero/skew.csv')
    #print list(OptionSkewDAO().get_sorted_weekly_skew())

