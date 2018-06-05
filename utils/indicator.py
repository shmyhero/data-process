

class MACD(object):

    @staticmethod
    def ema(n, current_price, previous_ema=None):
        if previous_ema is None:
            return current_price
        else:
            return previous_ema * ( n -1 ) /( n +1) + current_price * 2/ (n + 1)

    @staticmethod
    def get_all_ema(price_list, n):
        previous_ema = None
        result = []
        for price in price_list:
            ema = MACD.ema(n, price, previous_ema)
            result.append(ema)
            previous_ema = ema
        return result

    @staticmethod
    def dif(ema_short, ema_long):
        return ema_short - ema_long

    @staticmethod
    def dea(current_dif, m=9, previous_dea=None):
        return MACD.ema(m, current_dif, previous_dea)

    @staticmethod
    def bar(dif, dea):
        return (dif - dea) * 2

    @staticmethod
    def get_new_macd(previous_ema_short, previous_ema_long, previous_dea, current_price, s=12, l=26, m=9):
        current_ema_short = MACD.ema(s, current_price, previous_ema_short)
        current_ema_long = MACD.ema(l, current_price, previous_ema_long)
        current_dif = MACD.dif(current_ema_short, current_ema_long)
        current_dea = MACD.dea(current_dif, m, previous_dea)
        current_bar = MACD.bar(current_dif, current_dea)
        return [current_ema_short, current_ema_long, current_dif, current_dea, current_bar]

    @staticmethod
    def get_all_macd(price_list, previous_ema_short=None, previous_ema_long=None, previous_dea=None, s=12, l=26, m=9):
        result = []
        [ema_short, ema_long, dif, dea, bar] = [previous_ema_short, previous_ema_long, None, previous_dea, None]
        for price in price_list:
            record = MACD.get_new_macd(ema_short, ema_long, dea, price, s, l, m)
            result.append(record)
            [ema_short, ema_long, dif, dea, bar] = record
        return result

# import talib
# import numpy


class RSI(object):

    @staticmethod
    def get_init_rsi(price_list):
        count = len(price_list)-1
        up_sum = 0
        down_sum = 0
        for i in range(count):
            delta = price_list[i+1] - price_list[i]
            if delta > 0:
                up_sum += delta
            else:
                down_sum -= delta
        up_ave = up_sum*1.0 / count
        down_ave = down_sum * 1.0 / count
        rsi = 100.0*up_sum/(up_sum + down_sum)
        return up_ave, down_ave, rsi

    @staticmethod
    def calc_new_rsi(time_period, delta, rsi_obj):
        if delta > 0:
            up = delta*1.0
            down = 0
        else:
            up = 0
            down = -delta*1.0
        previous_up, previous_down, previous_rsi = rsi_obj
        new_up = up/time_period + previous_up*(time_period-1)/time_period
        new_down = down/time_period + previous_down * (time_period - 1) / time_period
        rsi = 100 * new_up/(new_up + new_down)
        return new_up, new_down, rsi

    @staticmethod
    def get_new_rsi(time_period, price, previous_price, rsi_object=None):
        delta = price-previous_price
        return RSI.calc_new_rsi(time_period, delta, rsi_object)

    @staticmethod
    def get_rsi(price_list, time_period):
        count = len(price_list)-1
        if count < 1 or count < time_period:
            return [None] * (count+1)
        else:
            rsi_list = [None] * time_period
            rsi_object = RSI.get_init_rsi(price_list[0:time_period+1])
            rsi_list.append(rsi_object[-1])
            previous_price = price_list[time_period]
            rest_price_list = price_list[time_period+1:]
            for price in rest_price_list:
                rsi_object = RSI.get_new_rsi(time_period, price, previous_price, rsi_object)
                previous_price = price
                rsi_list.append(rsi_object[-1])
            return rsi_list


    # @staticmethod
    # def get_rsi2(price_list, time_period):
    #     rsi = talib.RSI(numpy.array(price_list), time_period)
    #     # print rsi
    #     return rsi


class SAR(object):
    """
    psar Parabolic SAR(stop and reverse))
    psar: (high_list, low_list, bull_p, af, sar)
    af: acceleration factor
    ep: extreme point
    iaf: increase affcleration facrtor
    """
    @staticmethod
    def get_new_sar(high, low, last_psar=None, bar_count=4, af0=0.02, iaf=0.02, max_af=0.2):
        if last_psar is None:
            return [high], [low], True, iaf, low
        else:
            (high_list, low_list, bull_p, af, sar) = last_psar
            last_high = max(high_list)
            last_low = min(low_list)
            if len(high_list) >= bar_count:
                new_high_list = high_list[1:] + [high]
                new_low_list = low_list[1:] + [low]
            else:
                new_high_list = high_list + [high]
                new_low_list = low_list + [low]
                return new_high_list, new_low_list, True, af0, min(new_low_list)
            new_high = max(new_high_list)
            new_low = min(new_low_list)
            if bull_p:
                ep = last_high
                new_sar = sar + af * (ep - sar)
                if new_low < new_sar:
                    return new_high_list, new_low_list, False, af0, new_high
                else:
                    if new_high > last_high:
                        af = min(af + iaf, max_af)
                    # if last_low < new_sar:
                    #     new_sar = last_low
                    return new_high_list, new_low_list, bull_p, af, new_sar
            else:
                ep = last_low
                new_sar = sar + af * (ep - sar)
                if new_high > new_sar:
                    return new_high_list, new_low_list, True, af0, new_low
                else:
                    if new_low < last_low:
                        af = min(af + iaf, max_af)
                    # if last_high > new_sar:
                    #     new_sar = last_high
                    return new_high_list, new_low_list, bull_p, af, new_sar

    @staticmethod
    def get_initial_sar(high_pirce_list, low_price_list, bar_count=4, af0=0.02, iaf=0.02, max_af=0.2):
        psar_list = []
        psar = None
        for i in range(len(high_pirce_list)):
            high = high_pirce_list[i]
            low = low_price_list[i]
            psar = SAR.get_new_sar(high, low, psar, bar_count, af0, iaf, max_af)
            psar_list.append(psar)
        return psar_list

    @staticmethod
    def get_all_sar(high_pirce_list, low_price_list, bar_count=4, af0=0.02, iaf=0.02, max_af=0.2):
        psar_list = SAR.get_initial_sar(high_pirce_list, low_price_list, bar_count, af0, iaf, max_af)
        bull_sar = map(lambda x: [x[2], x[-1]], psar_list)
        for i in range(bar_count-1):
            bull_sar[i] = [None, None]
        return bull_sar




if __name__ == '__main__':
    # print MACD.get_all_macd([106.1, 26.59, 55.09, 56.1, 34.44, 45.29, 41.92])
    # print MACD.get_all_ema([106.1, 26.59, 55.09, 56.1, 34.44, 45.29, 41.92], 3)
    psar = SAR.get_new_sar(31.1, 25.92)
    print psar
    psar = SAR.get_new_sar(34.21, 34.21, psar)
    print psar
    psar = SAR.get_new_sar(37.63, 37.63, psar)
    print psar
    psar = SAR.get_new_sar(41.39, 41.39, psar)
    print psar
    psar = SAR.get_new_sar(45.53, 45.53, psar)
    print psar
    psar = SAR.get_new_sar(50.08, 50.08, psar)
    print psar
    print SAR.get_all_sar([31.1, 34.21, 37.63, 41.39, 45.53, 50.08, 55.09],
                          [25.92, 34.21, 37.63, 41.39, 45.53, 50.08, 55.09])