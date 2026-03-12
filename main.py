import requests
from pyquery import PyQuery as pq


def getpages():
    r = requests.get("https://books.toscrape.com/index.html")
    doc = pq(r.content)
    pages = doc("li.current").text()
    pages = pages.split(" of ")
    pages = pages[1]
    return int (pages)
##  aka: return int(doc("li.current").text().split(" of ")[1])

max_pages = getpages()

print(max_pages)
