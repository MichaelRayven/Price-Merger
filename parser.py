import json
import re
import requests
from threading import Thread
from bs4 import BeautifulSoup


class ParserThread(Thread):
    def __init__(self, url):
       Thread.__init__(self)
       self.url = url
       self._return = None
       
    def run(self):
        print(f"[INFO] Parsing: {self.url}")
        status, html = self.fetch_url(self.url)
        if not status: return
        status, data = self.get_page_data(html)
        if not status: return
        self._return = data
        
    def join(self):
        Thread.join(self)
        return self._return
        
    def get_page_data(self, html_doc):
        soup = BeautifulSoup(html_doc, "html.parser")
        script_tags = soup.select(".tabs-content>div script")
        if script_tags is None or len(script_tags) < 2: return (False, None)
        
        script_text = script_tags[1].getText()
        match = re.search(r"\"data\":(\[.*\])", script_text, flags=re.MULTILINE|re.DOTALL)
        if match is None: return (False, None)
        
        data = json.loads(match.group(1))
        return (True, data)

    def fetch_url(self, url: str):
        req = requests.get(url)
        if 200 >= req.status_code < 300:
            return (True, req.content)
        else:
            return (False, None)


class Parser:
    def __init__(self, url_list: list) -> None:
        self._urls = url_list
        print(f"[INFO] Parsing {len(url_list)} URLs")

    def parse_data(self) -> list:
        self._data = []
        for url in self._urls:
            self.__process_url(url)
        print(f"[INFO] Finished parsing {len(self._data)}")
        return self._data

    def __process_url(self, url):
        print(f"[INFO] Parsing: {url}")
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
    