import json
import re
import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url_list: list) -> None:
        self.urls = url_list

    def parse_data(self) -> list:
        data = []
        for url in self.urls:
            (status, html) = self.__fetch_url(url)
            if not status: continue
            (status, data) = self.__get_page_data(html)
            if not status: continue
            data.append(data)
        return data

    def __get_page_data(self, html_doc):
        soup = BeautifulSoup(html_doc, "html.parser")
        script_tags = soup.select(".tabs-content>div script")
        if script_tags is None or len(script_tags) < 2: return (False, None)
        
        script_text = script_tags[1].getText()
        match = re.search(r"\"data\":(\[.*\])", script_text, re.MULTILINE)
        if match is None: return (False, None)
        
        data = json.loads(match.group())
        return (True, data)

    def __fetch_url(self, url: str):
        req = requests.get(url)
        if 200 >= req.status_code < 300:
            return (True, req.content)
        else:
            return (False, None)
    