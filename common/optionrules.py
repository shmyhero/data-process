
class OptionRules(object):

    def __init__(self):
        pass

    @staticmethod
    def find_monthly_option_dates(expiration_dates):
        for expiration_date in expiration_dates:
            if expiration_date.weekday() == 4 and 14 < expiration_date.day < 22:
                yield expiration_date

