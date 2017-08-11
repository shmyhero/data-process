import datetime
import calendar
import json


class Credit(object):

    def __init__(self, year, month, values):
        self.year = year
        self.month = month
        self.date_str = Credit.get_last_date(year, month)

        self.margin_debt = int(values[0].replace(',', ''))
        self.cash_accounts = None #free_credit_cash_accounts
        self.credit_balance = None #credit_balance_in_margin_accounts
        if len(values) > 1:
            self.cash_accounts = int(values[1].replace(',', ''))
        if len(values) > 2:
            self.credit_balance = int(values[2].replace(',', ''))


    #TODO: change mapping to 'Januarary' : [1, 31]
    @staticmethod
    def get_last_date(year, month):
        dic = {'January': '-01-31',
               'February': '-02-28',
               'March': '-03-31',
               'April': '-04-30',
               'May': '-05-31',
               'June': '-06-30',
               'July': '-07-31',
               'August': '-08-31',
               'September': '-09-30',
               'October': '-10-31',
               'November': '-11-30',
               'December': '-12-31',
        }
        date_str = '%s%s' % (year, dic[month])
        if calendar.isleap(int(year)) and month == 'February':
            date_str = date_str.replace('28', '29')
        return date_str

    def to_json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.to_json()

    def to_dict(self):
        return {
            'date': datetime.datetime.strptime(self.date_str, '%Y-%m-%d'),
            'year': self.year,
            'month': self.month,
            'margin_debt': self.margin_debt,
            'cash_accounts': self.cash_accounts,
            'credit_balance': self.credit_balance
        }