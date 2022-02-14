import json
import random
import re
import asyncio
import ssl
from bs4 import BeautifulSoup
import aiohttp


class Parser:
    def __init__(self, url_list: list) -> None:
        self._urls = url_list
        print(f"[INFO] Recieved {len(url_list)} URLs")

    def parse_data(self) -> list:
        print("[INFO] Fetching URLs")
        loop = asyncio.get_event_loop()
        responses = loop.run_until_complete(self.get_documents(self._urls, loop))
        loop.run_until_complete(asyncio.sleep(10))
        loop.close()
        
        data_list = []
        print("[INFO] Done fetching, now parsing")
        for document in responses:
            if isinstance(document, str):
                (status, result) = self.parse_page(document)
                if status: data_list.append(result)
        
        print(f"[INFO] Succssfully parsed {len(data_list)} URLs")
        return data_list

    def parse_page(self, document):
        soup = BeautifulSoup(document, "html.parser")
        script_tags = soup.select(".tabs-content>div script")
        if script_tags is None or len(script_tags) < 2: return (False, None)
        
        script_text = script_tags[1].getText()
        match = re.search(r"\"data\":(\[.*\])", script_text, flags=re.MULTILINE|re.DOTALL)
        if match is None: return (False, None)
        
        data = json.loads(match.group(1))
        return (True, data)

    async def get_documents(self, urls, loop):
        connector = aiohttp.TCPConnector(limit=15)
        async with aiohttp.ClientSession(loop=loop, connector=connector) as session: 
            responses = await asyncio.gather(*[self.fetch(url, session) for url in urls], return_exceptions=True)
            return responses

    async def fetch(self, url, session: aiohttp.ClientSession):
        # delay = round((random.random() + 0.05) * 3, 2)
        # print(f"[INFO] Fetching {url} with a delay of: {delay}s...")
        # await asyncio.sleep(delay)
        async with session.get(url, ssl=ssl.SSLContext()) as response:
            if response.status == 200:
                print(f"[INFO] Fetched: {url}, success" + '\033[92m')
                return await response.text()
            else:
                print(f"[INFO] Fetched: {url}, failed" + '\033[91m')
            