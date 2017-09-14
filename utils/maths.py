from decimal import Decimal


def half_adjust_round(num, length):
    template = '{:.%sf}'%length
    return float(template.format(Decimal(num)))


