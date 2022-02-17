from math import floor
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import urllib.parse


class Crawler():
    def __init__(self, query: str, target_url: str) -> None:
        self._query = query
        self._target = target_url
        self._data = []

    def get_urls_list(self, count: int):
        if len(self._data) >= count: self._data[0:count]
        
        self._driver = self.__init_driver()
        with self._driver:
            try:
                print("[INFO] Getting URLs!")
                self.__get_urls(count)
            except Exception as err:
                print(err)
                return []
        return self._data[0:count]

    def __get_urls(self, count):
        link_elements = self.__recover_progress()
        while len(self._data) < count:
            for link in link_elements:
                url = link.get_attribute("href")
                print(f"[INFO] Adding: {url} to the list...")
                self._data.append(url)
                
            next = self.__next_page()
            if not next: break
            
            link_elements = self._driver.find_elements(By.XPATH, "//div[contains(@class, 'list-item--goods')]//a[@data-url]")
            if len(link_elements) == 0: break
        print("[INFO] URLs collected!")

    def __init_driver(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(5)
        if self._target:
            driver.get(self._target)
        else:
            driver.get(f"https://www.e-katalog.ru/ek-list.php?search_={self._query}")
            WebDriverWait(driver, 10).until_not(
                EC.url_to_be(f"https://www.e-katalog.ru/ek-list.php?search_={self._query}"))
        print("[INFO] Driver initialized!")
        return driver

    def __next_page(self):
        print("[INFO] Getting next page...", end=" ")
        button_element = self._driver.find_elements(
            By.CSS_SELECTOR, ".ib.select+a")
        if len(button_element) > 0:
            button_element[0].click()
            print("Success!")
            return True
        else:
            print("Fail.")
            return False

    def __recover_progress(self):
        if len(self._data) > 0:
            links_on_page = self._driver.find_elements(By.XPATH, "//div[contains(@class, 'list-item--goods')]//a[@data-url]")
            page = floor(self._data / len(links_on_page))

            if page == 0: return links_on_page[len(self._data):]

            button_element = self._driver.find_element(By.CSS_SELECTOR, ".ib.select")
            if button_element is not None:
                button_element.click()
            else:
                return []

            self._driver.get(self._driver.current_url + f"&page_={page}")
            links_on_current_page = self._driver.find_elements(By.XPATH, "//div[contains(@class, 'list-item--goods')]//a[@data-url]")

            if len(links_on_current_page) == 0:
                return []
            else:
                return links_on_current_page[len(self._data) % len(links_on_page):]
        return self._driver.find_elements(By.XPATH, "//div[contains(@class, 'list-item--goods')]//a[@data-url]")
