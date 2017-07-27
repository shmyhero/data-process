import json
from datetime import datetime


class BaseEntity(object):

    def __init__(self):
        pass

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def fix_na(v):
        if v == 'N\/A' or v == 'NA' or v == 'N/A':
            return None
        else:
            return v

    @staticmethod
    def parse_float(value):
        try:
            if value:
                value = value.replace(',', '')
                value = value.replace('s', '')
                value = value.replace('unch', '0')
                return float(value)
            else:
                return None
        except:
            return None

    @staticmethod
    def parse_date(value):
        try:
            if value:
                date = datetime.strptime(value, '%m/%d/%y')
                return date
            else:
                return None
        except:
            return None

    @staticmethod
    def parse_for_entity(fn, entity, fields):
        for field in fields:
            value = getattr(entity, field)
            setattr(entity, field, fn(value))


if __name__ == '__main__':
    print datetime.strptime('07/28/17', '%m/%d/%y')



