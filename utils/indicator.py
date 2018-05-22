

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


if __name__ == '__main__':
    # print MACD.get_all_macd([106.1, 26.59, 55.09, 56.1, 34.44, 45.29, 41.92])
    print MACD.get_all_ema([106.1, 26.59, 55.09, 56.1, 34.44, 45.29, 41.92], 3)
