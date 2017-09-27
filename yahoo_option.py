from ingestion.yahooscraper import YahooScraper
from dataaccess.yahoooptionparser import YahooOptionParser


if __name__ == '__main__':
    YahooScraper.ingest_all_options(['^VIX'])
    YahooOptionParser.save_to_db()
    YahooOptionParser.update_delta()

