import json
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
        url_list = []
        try:
            with open(os.path.abspath(url_list_path), "r") as file:
                data = json.loads(file.read())
                if isinstance(data, list):
                    url_list = data
                else:
                    raise Exception("[Error] Insuffisient data type")
        except Exception as err:
            print(err)
            return
        
        parser = Parser(url_list)
    else:
        print("[INFO] Creating Crawler")
        crawler = Crawler(search_query)
        parser = Parser(crawler.list_urls(int(url_quantity)))
    
    data_list = parser.parse_data()

    print("[INFO] Analysing the data")
    analyser = DataAnalyser(data_list, data_preference, int(data_threshold))
    data = analyser.pack_data()
    
    GraphBuilder(data)


if __name__ == "__main__":
    main()
