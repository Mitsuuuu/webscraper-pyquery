from tqdm import tqdm
import requests
from pyquery import PyQuery as pq

def book_name_collection(doc):
    name = str()
    for link in tqdm(doc("h3>a"), desc="Books:", position=1, leave=False):
        link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]
        r = requests.get(link)
        doc = pq(r.content)
        name = (doc("h1").text())
    return name