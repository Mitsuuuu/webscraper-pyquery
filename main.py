from tqdm import tqdm
import requests
from pyquery import PyQuery as pq
import pandas as pd

pd.set_option("display.max_colwidth", None)

# Funktion: Anzahl der Seiten herausfinden
def getpages():
    r = requests.get("https://books.toscrape.com/index.html")
    doc = pq(r.content)

    text = doc("li.current").text()      # z.B. "Page 1 of 50"
    pages = text.split(" of ")           # ["Page 1", "50"]

    return int(pages[1])


max_pages = getpages()

# Liste für alle Bücher
books = []

zahl = int(input("Aktion auswählen: "))

match zahl:
    case 1:
        for page in tqdm(range(1, 2), desc="Seiten"):

            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            r = requests.get(url)
            doc = pq(r.content)

            for link in tqdm(doc("h3 > a"), desc="Bücher", leave=False):

                book_link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]

                r = requests.get(book_link)
                doc = pq(r.content)

                title = doc("h1").text()

                # Daten zur Liste hinzufügen
                books.append({
                    "Titel": title,
                    "Link": book_link
                })


# DataFrame aus der Liste erstellen
books_df = pd.DataFrame(books)

print("\nGefundene Bücher:\n")
print(books_df)