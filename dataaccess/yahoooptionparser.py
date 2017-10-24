import datetime
import json
from utils.iohelper import get_sub_files, read_file_to_string
from utils.stringhelper import string_fetch
from utils.listhelper import list_to_hash
from common.tradetime import TradeTime
from common.pathmgr import PathMgr
from dataaccess.basedao import BaseDAO
from common.optioncalculater import OptionCalculater
from dataaccess.optiondao import OptionDAO
from dataaccess.vixdao import VIXDAO
from entities.option import Option


class YahooOptionParser(object):

    @staticmethod
    def json_obj_to_option(json_obj, underling_symbol):
        option = Option()
        option.underlingSymbol = underling_symbol
        option.symbol = json_obj['contractSymbol']
        option.volatility = json_obj['impliedVolatility']['raw']*100
        option.expirationDate = datetime.datetime.strptime(json_obj['expiration']['fmt'], '%Y-%m-%d')
        option.strikePrice = json_obj['strike']['raw']
        option.lastPrice = json_obj['lastPrice']['raw']
        option.openInterest = json_obj['openInterest']['raw']
        option.priceChange = json_obj['percentChange']['raw']
        option.askPrice = json_obj['ask']['raw']
        option.volume = json_obj['volume']['raw']
        option.tradeTime = datetime.datetime.strptime(json_obj['lastTradeDate']['fmt'],  '%Y-%m-%d')
        option.bidPrice = json_obj['bid']['raw']
        if 'C' in option.symbol:
            option.optionType = 'Call'
        else:
            option.optionType = 'Put'
        option.daysToExpiration = (option.expirationDate - option.tradeTime).days
        return option

    @staticmethod
    def parse_raw_file(raw_file):
        content = read_file_to_string(raw_file)
        underling_symbol = string_fetch(content, '<title>', ' Option')
        sub_content = string_fetch(content, '"underlyingSymbol\":\"%s\"},\"contracts\":'%underling_symbol, ',\"displayed\"')
        json_content = sub_content + '}'
        json_obj = json.loads(json_content)
        objs = json_obj['calls']
        put_objs = json_obj['puts']
        objs.extend(put_objs)
        for obj in objs:
            yield YahooOptionParser.json_obj_to_option(obj, underling_symbol)

    @staticmethod
    def parse_raw_data(subpath=None):
        subpath = subpath or datetime.date.today().strftime('%Y-%m-%d')
        dir = PathMgr.get_yahoo_option_symbol_dir('^VIX', subpath)
        files = get_sub_files(dir, 'html')
        options = []
        for file in files:
            options.extend(list(YahooOptionParser.parse_raw_file(file)))
        return options

    @staticmethod
    def save_to_db():
        OptionDAO().insert(YahooOptionParser.parse_raw_data())

    @staticmethod
    def update_delta(risk_free_interest_rate=0.005):
        date_price_records = VIXDAO().get_vix_price_by_symbol('VIY00')
        date_hv_lst = OptionCalculater.get_year_history_volatility_list(date_price_records)
        date_price_dic = list_to_hash(date_price_records)
        date_hv_dic = list_to_hash(date_hv_lst)
        option_dao = OptionDAO()
        vix_option_records = option_dao.get_vix_options()
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        count = 0
        for (symbol, trade_date, left_days, strike_price, option_type) in vix_option_records:
            underlying_price = date_price_dic.get(trade_date)
            sigma = date_hv_dic.get(trade_date)
            if underlying_price is not None and sigma is not None:
                delta = OptionCalculater.get_delta(underlying_price, strike_price, left_days, risk_free_interest_rate, sigma, option_type[0:1].lower())
                option_dao.update_delta_for_vix_options(symbol, trade_date, delta, cursor)
                count += 1
                if count == 1000:
                    conn.commit()
                    count = 0
        conn.commit()
        conn.close()


if __name__ == '__main__':
    #YahooOptionParser.save_to_db()
    YahooOptionParser.update_delta()
