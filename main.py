from tqdm import tqdm
import requests
from pyquery import PyQuery as pq
import pandas as pd

# Anzeigeoptionen auf unbegrenzte Länge setzen
pd.set_option('display.max_colwidth', None)

def getpages():
    r = requests.get("https://books.toscrape.com/index.html")
    doc = pq(r.content)
    pages = doc("li.current").text()
    pages = pages.split(" of ")
    return int(pages[1])

max_pages = getpages()

# DataFrame initialisieren
books_df = pd.DataFrame(columns=["Titel", "Link"])

# Benutzeraktion
zahl = int(input("Aktion auswählen:"))
match zahl:
    case 1:
        for page in tqdm(range(1, 2), desc="Seiten", position=0):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            r = requests.get(url)
            doc = pq(r.content)

            for link in tqdm(doc("h3 > a"), desc="Bücher", position=1, leave=False):
                book_link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]
                r = requests.get(book_link)
                doc = pq(r.content)
                title = doc("h1").text()

                # Neue Zeile zum DataFrame hinzufügen
                books_df = pd.concat([books_df, pd.DataFrame([{"Titel": title, "Link": book_link}])], ignore_index=True)

# Index auf 1-basierte Nummerierung setzen
books_df.index = range(1, len(books_df) + 1)

# Ausgabe linksbündig mit Index
print(f"\n{len(books_df)} Bücher gefunden.\n")

# Länge der längsten Titel bestimmen
max_len_title = books_df["Titel"].str.len().max() + 2  # +2 für Abstand

# Überschrift mit Index
print(f"{'Nr':<4}{'Titel':<{max_len_title}}Link")
print("-" * (4 + max_len_title + 60))  # Trennlinie

# Daten ausgeben
for idx, row in books_df.iterrows():
    print(f"{idx:<4}{row['Titel']:<{max_len_title}}{row['Link']}")