import json
import re
import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url_list: list) -> None:
        self.urls = url_list
        self.data = []

    def parse_data(self):
        for url in self.urls[len(self.data):]:
            html_doc = self.__fetch_url(url)
            page_data = self.__get_page_data(html_doc)
            if page_data is None: continue
            self.data.append(page_data)
        return self.data

    def __get_page_data(self, html_doc):
        soup = BeautifulSoup(html_doc, "html.parser")
        try: 
            script_tag = soup.select(".tabs-content>div script")[1]
        except Exception:
            return None
        code = script_tag.getText()
        matches = re.findall(r"\"data\":(\[.*\])", code, re.MULTILINE)
        return json.loads(matches[0])

    def __fetch_url(self, url: str):
        req = requests.get(url)
        if 200 >= req.status_code < 300:
            return req.content
        else:
            return ""
