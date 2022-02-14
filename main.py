import asyncio
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
    url_list_path = os.environ["URL_LIST_PATH"]
    search_query = os.environ["SEARCH_QUERY"]
    url_quantity = os.environ["URLS_QUANTITY"]
    data_preference = os.environ["DATA_PREFERENCE"]
    data_threshold = os.environ["DATA_THRESHOLD"]

    if url_list_path != "":
        print("[INFO] Loading URLs from list")
        url_list = load_json(url_list_path)
        parser = Parser(url_list)
    else:
        print("[INFO] Creating Crawler")
        crawler = Crawler(search_query)
        url_list = crawler.get_urls_list(int(url_quantity))
        parser = Parser(url_list)
        
    
    data_list = parser.parse_data()
    print("[INFO] Analysing the data")

    analyser = DataAnalyser(data_list, data_preference, int(data_threshold))
    data = analyser.pack_data()
    
    GraphBuilder(data)


if __name__ == "__main__":
    main()
