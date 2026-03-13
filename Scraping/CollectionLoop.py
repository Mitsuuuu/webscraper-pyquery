from tqdm import tqdm
import requests
from pyquery import PyQuery as pq

def book_name_collection(doc):
    names_list = []
    for link in tqdm(doc("h3>a"), desc="Books:", position=1, leave=False):
        link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]
        r = requests.get(link)
        doc = pq(r.content)
        name = (doc("h1").text())
        names_list.append(name)
    return names_list # Gibt eine Liste mit den Namen einer einzelnen Seite zurück