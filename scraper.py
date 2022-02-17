import os
from queue import Queue
import re
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv


class Scraper():
    def __init__(self, quantity: int, query="", target_url="") -> None:
        self._pages = Queue()
        self._output = []
        self._quantity = quantity

        if target_url:
            self._pages.put(target_url)
        else:
            query = re.sub(r"\s", r"%20", query)
            self._pages.put(
                f"https://www.e-katalog.ru/ek-list.php?search_={query}")

    def scrape(self):
        self.__get_pages()
        return self._output[:self._quantity]

    def __get_pages(self):
        while not self._pages.empty() and len(self._output) < self._quantity:
            url = self._pages.get()
            page = self.__fetch_page(url)
            soup = BeautifulSoup(page, 'html.parser')
            next_page = soup.select_one(".ib.select+a")
            divs = soup.select("div.list-item--goods")
            if len(divs) > 24:
                divs = divs[1::2]
            if len(divs) == 0:
                break
            for div in divs:
                link = div.find("a", attrs={"data-url": True})
                self._output.append("https://www.e-katalog.ru" + link["href"])
            if next_page is not None:
                self._pages.put("https://www.e-katalog.ru" + next_page["href"])

    def __fetch_page(self, url):
        try_count = 0
        while try_count < 3:
            try_count += 1
            resp = requests.get(url)
            if resp.status_code in (200, 429):
                return resp.text
