import json
import re
import requests
import threading
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url_list: list) -> None:
        self._urls = url_list

    def parse_data(self) -> list:
        self._data = []
        threads = []
        for url in self._urls:
            thread = threading.Thread(target=self.__process_url, args=[url])
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
            
        print("[INFO] Parsing finished")
        return self._data

    def __process_url(self, url):
        status, html = self.__fetch_url(url)
        if not status: return
        status, data = self.__get_page_data(html)
        if not status: return
        self._data.append(data)

    def __get_page_data(self, html_doc):
        soup = BeautifulSoup(html_doc, "html.parser")
        script_tags = soup.select(".tabs-content>div script")
        if script_tags is None or len(script_tags) < 2: return (False, None)
        
        script_text = script_tags[1].getText()
        match = re.search(r"\"data\":(\[.*\])", script_text, flags=re.MULTILINE|re.DOTALL)
        if match is None: return (False, None)
        
        data = json.loads(match.group(1))
        return (True, data)

    def __fetch_url(self, url: str):
        req = requests.get(url)
        if 200 >= req.status_code < 300:
            return (True, req.content)
        else:
            return (False, None)
    