

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


class RSI(object):

    @staticmethod
    def get_rsi(price_list):
        if price_list < 2:
            return 50
        positive_sum = 0
        negative_sum = 0
        for i in range(len(price_list)-1):
            delta = price_list[i+1] - price_list[i]
            if delta > 0:
                positive_sum += delta
            else:
                negative_sum -= delta
        if positive_sum == negative_sum:
            return 50
        else:
            return 100.0*positive_sum/(positive_sum + negative_sum)


class SAR(object):
    """
    psar Parabolic SAR(stop and reverse))
    psar: (last_high, last_low, bull_p, ep, af, sar)
    af: acceleration factor
    ep: extreme point
    """
    @staticmethod
    def get_new_sar(high, low, last_psar=None, af0=0.02, iaf=0.02, max_af=0.2):
        if last_psar is None:
            return high, low, True, low, af0, low
        else:
            (last_high, last_low, bull_p, ep, af, sar) = last_psar
        if bull_p:
            new_sar = sar + af * (ep - sar)
            if low < new_sar:
                return high, low, False, low, af0, high
            else:
                if high > ep:
                    ep = high
                    af = min(af + iaf, max_af)
                if last_low < new_sar:
                    new_sar = last_low
                return high, low, bull_p, ep, af, new_sar
        else:
            new_sar = sar + af * (ep - sar)
            if high > new_sar:
                return high, low, True, high, af0, low
            else:
                if low < ep:
                    ep = low
                    af = min(af + iaf, max_af)
                if last_high > new_sar:
                    new_sar = last_high
                return high, low, bull_p, ep, af, new_sar

    @staticmethod
    def get_all_sar(high_pirce_list, low_price_list, af0=0.02, iaf=0.02, max_af=0.2):
        psar_list = []
        psar = None
        for i in range(len(high_pirce_list)):
            high = high_pirce_list[i]
            low = low_price_list[i]
            psar = SAR.get_new_sar(high, low, psar, af0, iaf, max_af)
            psar_list.append(psar)
        return map(lambda x: [x[2], x[-1]], psar_list)






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