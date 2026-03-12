from tqdm import tqdm

import requests
from pyquery import PyQuery as pq


def getpages():
    r = requests.get("https://books.toscrape.com/index.html")
    doc = pq(r.content)
    pages = doc("li.current").text()
    pages = pages.split(" of ")
    pages = pages[1]
    return int (pages)

max_pages = getpages()
all_books = []

for page in tqdm(range(1, max_pages + 1), desc="Pages:", position=0):
    url = "https://books.toscrape.com/catalogue/page-{}.html".format(page)
    r = requests.get(url="https://books.toscrape.com/catalogue/page-{}.html".format(page))
    doc = pq(r.content)
    for link in tqdm(doc("h3>a"), desc="Books:",position=1, leave=False):
        link = "https://books.toscrape.com/catalogue/"+link.attrib["href"]
        r = requests.get(link)
        doc = pq(r.content)
        all_books.append(doc("h1").text())
print(all_books)






