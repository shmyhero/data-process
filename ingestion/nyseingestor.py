
from utils.stringhelper import string_fetch
from utils.httphelper import HttpHelper
from entities.nysecredit import Credit


class NYSEIngestor(object):

    NYSE_CREDIT_URL = 'http://www.nyxdata.com/nysedata/asp/factbook/viewer_edition.asp?mode=tables&key=50&category=8'

    def __init__(self):
        pass

    @staticmethod
    def parse_table(sub_content):
        year = string_fetch(sub_content, '($ in mils.), ', '\r\n')
        sub_content = string_fetch(sub_content, 'Credit balances in margin accounts', '</table>')
        item_contents = sub_content.split('<b>')[1:]
        credits = []
        for item_content in item_contents:
            month_str = string_fetch(item_content, '', '</td>')
            item_values = item_content.split('align=right >')[1:]
            values = map(lambda x: string_fetch(x, '$', '</td>'), item_values)
            if values[0] != '':
                credit = Credit(year, month_str, values)
                credits.append(credit)
        return credits

    @staticmethod
    def ingest_credit():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        content = HttpHelper.http_get(NYSEIngestor.NYSE_CREDIT_URL, headers)
        content = string_fetch(content, ' View All Years', '')
        sub_contents = content.split('Securities market credit')[1:]
        all_credits = []
        for sub_content in sub_contents:
            credits = NYSEIngestor.parse_table(sub_content)
            all_credits.extend(credits)
        return all_credits


class NYSEIngestor2(object):

    NYSE_CREDIT_URL = 'http://www.finra.org/investors/margin-statistics'

    def __init__(self):
        pass

    @staticmethod
    def parse_table(sub_content):
        item_contents = sub_content.split('<tr')[2:-1]
        # print item_contents
        credits = []
        for item_content in item_contents:
            item_values = item_content.split('\n\t')[:-1]
            values = map(lambda x: string_fetch(x, 'top\">', '</td>'), item_values)
            # print values
            year = int(string_fetch(values[0], '-', '')) + 2000
            month_str = string_fetch(values[0], '', '-')
            credit = Credit(year, month_str, values[1:])
            credits.append(credit)
        return credits

    @staticmethod
    def ingest_credit():
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        content = HttpHelper.http_get(NYSEIngestor2.NYSE_CREDIT_URL)
        content = string_fetch(content, '<h2>FINRA Statistics<sup>2</sup> (shown in $ millions)</h2>', '<p>1 Note that')
        sub_contents = content.split('<table')[1:]
        all_credits = []
        for sub_content in sub_contents:
            credits = NYSEIngestor2.parse_table(sub_content)
            all_credits.extend(credits)
        return all_credits



if __name__ == '__main__':
    # credits = NYSEIngestor.ingest_credit()
    # credits = [Credit(2017, 'May', ['11,21', '22,777', '58,098'])]
    # from dataaccess.nysecreditdao import NYSECreditDAO
    # NYSECreditDAO().save(credits)
    #for credit in credits:
    #    print credit
    #pass
    credits = NYSEIngestor2.ingest_credit()
    from dataaccess.nysecreditdao import NYSECreditDAO
    NYSECreditDAO().save(credits)