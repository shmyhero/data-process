import pandas as pd
from entities.nysecredit import Credit
from dataaccess.basedao import BaseDAO


class NYSECreditDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def save(self, credits):
        query_template = """insert into nyse_credit (lastDate,the_year,the_month,margin_debt,cash_accounts,credit_balance) values
                         (str_to_date('{}', '%Y-%m-%d'),{},{},{},{},{})
                         on duplicate key update margin_debt = {}, cash_accounts = {}, credit_balance = {}"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()

        for credit in credits:
            query = BaseDAO.mysql_format(query_template, credit.date_str, credit.year, credit.month, credit.margin_debt, credit.cash_accounts, credit.credit_balance, credit.margin_debt, credit.cash_accounts, credit.credit_balance)
            # print query
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def get_all_margin_debt(self, start_date_str='1993-01-01'):
        query_template = """select {} from nyse_credit where lastDate >= str_to_date('{}', '%Y-%m-%d') order by lastDate"""
        columns = ['lastDate', 'margin_debt']
        query = BaseDAO.mysql_format(query_template, ', '.join(columns), start_date_str)
        rows = self.select(query)
        df = pd.DataFrame(rows)
        df.columns = columns
        return df


if __name__ == '__main__':
    #print BaseDAO.python_value_to_sql_value(0.0)
    #pass
    print NYSECreditDAO().get_all_margin_debt()