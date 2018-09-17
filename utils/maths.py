from decimal import Decimal
import numpy as np
import pandas as pd


def half_adjust_round(num, length):
    template = '{:.%sf}'%length
    return float(template.format(Decimal(num)))


def get_sharp_ratio(price_list, risk_free_rate=0.03, year_window = 252):
    delta_price_list = pd.Series(price_list).diff()
    ave_return = delta_price_list.mean()*year_window
    annual_vol = np.std(price_list)*np.sqrt(year_window)
    return (ave_return - risk_free_rate)/annual_vol


if __name__ == '__main__':
    # print get_sharp_ratio([1, 0.9, 0.8, 0.7])
    print get_sharp_ratio([1, 1.0002, 1.0005, 1.0007])