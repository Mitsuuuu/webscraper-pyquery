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
all_names = []
anzahl_eintraege = 0
zahl = int (input("Aktion auswählen:"))
match zahl:
    case 1:
        for page in tqdm(range(1, 2), desc="Pages:", position=0):
            url = "https://books.toscrape.com/catalogue/page-{}.html".format(page)
            r = requests.get(url="https://books.toscrape.com/catalogue/page-{}.html".format(page))
            doc = pq(r.content)
            for link in tqdm(doc("h3>a"), desc="Books:", position=1, leave=False):
                link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]
                r = requests.get(link)
                doc = pq(r.content)
                all_names.append(doc("h1").text())
                anzahl_eintraege += 1

print(f"{anzahl_eintraege} Bücher gefunden.")
print(all_names)







