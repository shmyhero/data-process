import datetime
import calendar
import json


class Credit(object):

    def __init__(self, year, month_str, values):
        self.year = year
        self.month = Credit.get_month_dic()[month_str][0]
        self.date_str = Credit.get_last_date(year, month_str)

        self.margin_debt = int(values[0].replace(',', ''))
        self.cash_accounts = None #free_credit_cash_accounts
        self.credit_balance = None #credit_balance_in_margin_accounts
        if len(values) > 1:
            self.cash_accounts = int(values[1].replace(',', ''))
        if len(values) > 2:
            self.credit_balance = int(values[2].replace(',', ''))

    @staticmethod
    def get_month_dic():
        dic = {'January': [1, 31],
               'February': [2, 28],
               'March': [3, 31],
               'April': [4, 30],
               'May': [5, 31],
               'June': [6, 30],
               'July': [7, 31],
               'August': [8, 31],
               'September': [9, 30],
               'October': [10, 31],
               'November': [11, 30],
               'December': [12, 31],
               'Jan': [1, 31],
               'Feb': [2, 28],
               'Mar': [3, 31],
               'Apr': [4, 30],
               'May': [5, 31],
               'Jun': [6, 30],
               'Jul': [7, 31],
               'Aug': [8, 31],
               'Sep': [9, 30],
               'Oct': [10, 31],
               'Nov': [11, 30],
               'Dec': [12, 31],
               }
        return dic

    @staticmethod
    def get_last_date(year, month):
        dic = Credit.get_month_dic()
        date_str = '%s-%02d-%s' % (year, dic[month][0], dic[month][1])
        if calendar.isleap(int(year)) and month in ['February', 'Feb']:
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