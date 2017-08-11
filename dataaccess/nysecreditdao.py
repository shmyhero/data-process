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


if __name__ == '__main__':
    #print BaseDAO.python_value_to_sql_value(0.0)
    pass