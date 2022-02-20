import json
from random import random
import re
import asyncio
import ssl
from bs4 import BeautifulSoup
import aiohttp
from async_retrying import retry


class Parser:
    def __init__(self, url_list: list) -> None:
        self._urls = url_list
        print(f"[INFO] Recieved {len(url_list)} URLs")

    def parse_data(self) -> list:
        print("[INFO] Fetching URLs")
        loop = asyncio.get_event_loop()
        responses = loop.run_until_complete(
            self.__get_documents(self._urls, loop))
        loop.run_until_complete(asyncio.sleep(1))
        loop.close()

        data_list = []
        print(f"[INFO] Done fetching {len(responses)} URLs, now parsing...")
        for document in responses:
            if isinstance(document, str):
                (status, result) = self.__parse_page(document)
                if status:
                    data_list.append(result)

        print(f"[INFO] Succssfully parsed {len(data_list)} URLs")
        return data_list

    def __parse_page(self, document):
        soup = BeautifulSoup(document, "html.parser")
        script_tags = soup.select(".tabs-content>div script")
        if script_tags is None or len(script_tags) < 2:
            return (False, None)

        script_text = script_tags[1].getText()
        match = re.search(
            r"\"data\":(\[.*\])", script_text, flags=re.MULTILINE | re.DOTALL)
        if match is None:
            return (False, None)

        data = json.loads(match.group(1))
        return (True, data)

    async def __get_documents(self, urls, loop):
        min_delay = 0.3
        max_delay = 3
        task_list = []
        connector = aiohttp.TCPConnector(limit=15, ssl=ssl.SSLContext())
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session:
            for url in urls:
                delay = random() * (max_delay - min_delay) + min_delay
                task = asyncio.create_task(self.__fetch(url, session))
                task_list.append(task)
                await asyncio.sleep(delay)
            responses = await asyncio.gather(*task_list, return_exceptions=True)
            return responses

    @retry(attempts=5)
    async def __fetch(self, url, session: aiohttp.ClientSession):
        async with session.get(url) as response:
            if response.status != 200:
                print(f"[INFO] Fetched: {url}, failed: {response.status}")
                raise Exception("Bad status code")
            print(f"[INFO] Fetched: {url}, success")
            return await response.text()
