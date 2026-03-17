from tqdm import tqdm
import requests
from pyquery import PyQuery as pq
from Scraping.CollectionLoop import book_name_collection


pages = 4

def page_loop():
    all_names = []
    for page in tqdm(range(1, pages + 1), desc="Pages:", position=0):
        r = requests.get(url="https://books.toscrape.com/catalogue/page-{}.html".format(page))
        doc = pq(r.content)
        all_names.append(book_name_collection(doc))
    return all_names # Gibt alle Namen in einer Liste zurück