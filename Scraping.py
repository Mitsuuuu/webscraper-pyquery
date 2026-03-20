import re
from tqdm import tqdm
import requests
from pyquery import PyQuery
import pandas as pd

def getpages():
    r = requests.get("https://books.toscrape.com/index.html")
    doc = PyQuery(r.content)
    pages = doc("li.current").text().split(" of ")[1]

    return int (pages)

def collection_loop():
    all_links = []
    all_titles = []
    all_prices = []
    all_UPCs = []
    all_mediatypes = []
    all_genres = []
    length_description = []
    size_thumbnail = []

    for page in tqdm(range(1, 2), desc="Pages:", position=0):
        r = requests.get(url="https://books.toscrape.com/catalogue/page-{}.html".format(page))
        doc = PyQuery(r.content)
        for link in tqdm(doc("h3>a"), desc="Books:", position=1, leave=False):
            link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]
            all_links.append(link)

            # Lade Website
            r = requests.get(link)
            doc = PyQuery(r.content)

            # Titel
            all_titles.append(doc("h1").text())

            # Preis, UPC, Medientyp
            tds = doc("td").text().split(" ")
            all_UPCs.append(tds[0])     #UPC
            all_mediatypes.append(tds[1])   #Medientyp
            all_prices.append(tds[3])   #Preis

            #Genre
            all_genres.append(doc(".breadcrumb > li > a").eq(2).text())

            #Länge Beschreibung
            words = (re.findall(r"\b[\w']+\b", doc("p").text()))
            length_description.append(len(words))

            #Größe Thumbnail
            image_link = "https://books.toscrape.com/"+ doc("img").attr["src"].split("../../")[1]
            response = requests.head(image_link)
            size_thumbnail.append((response.headers.get('Content-Length', "Filesize nicht gefunden")))


    return all_links, all_titles, all_prices, all_genres, all_mediatypes, all_UPCs, length_description, size_thumbnail

def lists_to_dataframe():
    all_links, all_titles, all_prices,all_genres, all_mediatypes, all_UPCs, length_description, size_thumbnail = collection_loop()

    df = pd.DataFrame({"Titel":              all_titles,
                       "Link":               all_links,
                       "Preis":              all_prices,
                       "Genre":              all_genres,
                       "Medientyp":          all_mediatypes,
                       "UPC":                all_UPCs,
                       "Länge_Beschreibung": length_description,
                       "Größe_Thumbnail":    size_thumbnail})

    return df