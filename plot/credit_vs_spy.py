import calendar
import json
import pandas as pd
from utils.stringhelper import string_fetch
from utils.httphelper import HttpHelper


class Credit(object):

    def __init__(self, year, month, values):

        self.date_str = self.get_last_date(year, month)
        #print year, month
        #print values
        #[self.margin_debt, self.free_credit_cash_accounts, self.credit_balances_in_margin_accounts] =\
        #    map(lambda x: int(x.replace(',', '')), values)
        self.margin_debt = int(values[0].replace(',', ''))

    def get_last_date(self, year, month):
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
        date_str = year + dic[month]
        if calendar.isleap(int(year)) and month == 'February':
            date_str = date_str.replace('28', '29')
        return date_str

    def to_json(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.to_json()

    def to_dict(self):
        return {
            'date': self.date_str,
            'margin_debt': self.margin_debt,
        }



def parse_table(sub_content):
    year = string_fetch(sub_content, '($ in mils.), ', '\r\n')
    sub_content = string_fetch(sub_content, 'Credit balances in margin accounts', '</table>')
    item_contents = sub_content.split('<b>')[1:]
    credits = []
    for item_content in item_contents:
        month = string_fetch(item_content, '', '</td>')
        item_values = item_content.split('align=right >')[1:]
        values = map(lambda x: string_fetch(x, '$', '</td>'), item_values)
        if values[0] != '':
            credit = Credit(year, month, values)
            credits.append(credit)
    return credits


def ingest_credit():
    content = HttpHelper.http_get('http://www.nyxdata.com/nysedata/asp/factbook/viewer_edition.asp?mode=tables&key=50&category=8')
    content = string_fetch(content, ' View All Years', '')
    sub_contents = content.split('Securities market credit')[1:]
    all_credits = []
    for sub_content in sub_contents:
        credits = parse_table(sub_content)
        all_credits.extend(credits)
    return all_credits



if __name__ == '__main__':
    credits = ingest_credit()
    df = pd.DataFrame.from_records([s.to_dict() for s in credits])
    print df