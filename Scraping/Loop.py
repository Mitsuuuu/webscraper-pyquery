from tqdm import tqdm
import requests
from pyquery import PyQuery


def collection_loop():
    all_links = []
    all_titles = []
    all_prices = []
    all_UPCs = []
    all_genres = []

    for page in tqdm(range(1, 2), desc="Pages:", position=0):
        r = requests.get(url="https://books.toscrape.com/catalogue/page-{}.html".format(page))
        doc = PyQuery(r.content)
        for link in tqdm(doc("h3>a"), desc="Books:", position=1, leave=False):
            link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]
            all_links.append(link)

            # Load Website
            r = requests.get(link)
            doc = PyQuery(r.content)

            # Titles
            all_titles.append(doc("h1").text())

            # All tds
            tds = doc("td").text().split(" ")
            all_UPCs.append(tds[0])
            all_genres.append(tds[1])
            all_prices.append(tds[3])
            


    return all_links, all_titles, all_prices, all_genres, all_UPCs