from jsonfile import load_json, save_json
import os
from dotenv import load_dotenv
from analyser import DataAnalyser

from crawler import Crawler
from graph import GraphBuilder
from parser import Parser


def main():
    load_dotenv()
    # Environmental variables
    os.environ['PATH'] += ";" + os.environ["DRIVER_PATH"]
    search_query = os.environ["SEARCH_QUERY"]
    url_quantity = os.environ["URLS_QUANTITY"]
    crawler_target = os.environ["TARGET_PAGE"]
    
    url_list_path = os.environ["URL_LIST_PATH"]
    url_dump_path = os.environ["URLS_DUMP_PATH"]
    data_list_path = os.environ["DATA_LIST_PATH"]
    data_dump_path = os.environ["DATA_DUMP_PATH"]
    
    data_preference = os.environ["DATA_PREFERENCE"]
    data_threshold = int(os.environ["DATA_THRESHOLD"])
    use_median = os.environ["USE_MEDIAN"]

    if data_list_path != "":
        print("[INFO] Loading data list from a file")
        data_list = load_json(data_list_path)
    elif url_list_path != "":
        print("[INFO] Loading URLs from a file")
        url_list = load_json(url_list_path)
    else:
        print("[INFO] Creating Crawler")
        crawler = Crawler(search_query, crawler_target)
        url_list = crawler.get_urls_list(int(url_quantity))
        if url_dump_path != "": save_json(url_dump_path, url_list)
        
        print("[INFO] Parsing URL list")
        parser = Parser(url_list)
        data_list = parser.parse_data()
        if data_dump_path != "": save_json(data_dump_path, data_list)
    
    print("[INFO] Analysing the data")
    
    analyser = DataAnalyser(data_list, data_preference, data_threshold, use_median)
    week_data = analyser.pack_into_weeks()
    month_data = analyser.pack_into_months()
    
    GraphBuilder(week_data, month_data)

if __name__ == "__main__":
    main()
