import requests
import re
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from utils.utils import parse_articles
from db.models import session

URL = "https://blog.python.org/"

data = requests.get(URL)
if data.ok:
    soup_data = BeautifulSoup(data.content, "html.parser")
else:
    raise Exception(f"{URL} return {data.status_code}")

links_by_year = re.findall(r"https://pythoninsider.blogspot.com/[0-9]{4}/(?!\d)", data.text)


async def main():
    async with aiohttp.ClientSession() as session:
        for link in links_by_year:
            async with session.get(link, ssl=False) as r:
                page_content = await r.text()
                page_soup = BeautifulSoup(page_content, "html.parser")
                await parse_articles(page_soup)


start_time = time.time()

asyncio.run(main())
print(f"Time 2 {time.time() - start_time}")

session.close()

