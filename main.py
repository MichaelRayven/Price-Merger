from jsonfile import load_json, save_json
import os
from dotenv import load_dotenv
from analyser import DataAnalyser

from scraper import Scraper
from graph import GraphBuilder
from parser import Parser


def main():
    load_dotenv()
    search_query = os.environ["SEARCH_QUERY"]
    url_quantity = int(os.environ["URLS_QUANTITY"])
    scraper_target = os.environ["TARGET_PAGE"]
    url_dump_path = os.environ["DUMP_URLS"]
    url_list_path = os.environ["URL_LIST_PATH"]
    data_preference = os.environ["DATA_PREFERENCE"]
    data_threshold = int(os.environ["DATA_THRESHOLD"])
    use_median = os.environ["USE_MEDIAN"]

    if url_list_path != "":
        print("[INFO] Loading URLs from list")
        url_list = load_json(url_list_path)
        parser = Parser(url_list)
    else:
        print("[INFO] Creating Scraper")
        s = Scraper(url_quantity, search_query, scraper_target)
        url_list = s.scrape()

        if url_dump_path:
            save_json(url_dump_path, url_list)

        parser = Parser(url_list)

    data_list = parser.parse_data()
    print("[INFO] Analysing the data")

    analyser = DataAnalyser(data_list, data_preference,
                            data_threshold, use_median)
    week_data = analyser.pack_into_weeks()
    month_data = analyser.pack_into_months()

    GraphBuilder(week_data, month_data)


if __name__ == "__main__":
    main()
