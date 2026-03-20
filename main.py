from tqdm import tqdm
import requests
from pyquery import PyQuery as pq
import mysql.connector
import pandas as pd
import re

pd.set_option("display.max_colwidth", None)


# DB connection
def datenbank_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="",
        database="WebscrapingDB"
    )

# Create tables
def create_tables():
    conn = datenbank_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Genre (
            Genre_ID INT AUTO_INCREMENT PRIMARY KEY,
            Genre_Name VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Medientypen (
            Medientyp_ID INT AUTO_INCREMENT PRIMARY KEY,
            Medientyp VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Artikel (
            Artikel_ID INT AUTO_INCREMENT PRIMARY KEY,
            Genre_ID INT NULL,
            Medientyp_ID INT NULL,
            Preis DECIMAL(6,2),
            Groesse_Beschreibung INT,
            UPC VARCHAR(50),
            Daten_menge_thumbnail INT,
            Buchtitel VARCHAR(200),
            Link VARCHAR(300) UNIQUE,
            FOREIGN KEY (Genre_ID) REFERENCES Genre(Genre_ID)
                ON DELETE SET NULL ON UPDATE CASCADE,
            FOREIGN KEY (Medientyp_ID) REFERENCES Medientypen(Medientyp_ID)
                ON DELETE SET NULL ON UPDATE CASCADE
        );
    """)

    conn.commit()
    conn.close()


# Get number of pages
def getpages(session):
    r = session.get("https://books.toscrape.com/index.html", timeout=5)
    doc = pq(r.content)
    text = doc("li.current").text()
    return int(text.split(" of ")[1])


# Scraping
def scrape_books(session, max_pages=50):
    books = []

    conn = datenbank_connection()
    cursor = conn.cursor()

    genre_cache = {}
    medientyp_cache = {}

    def get_genre_id(name):
        if not name:
            return None
        if name in genre_cache:
            return genre_cache[name]

        cursor.execute("SELECT Genre_ID FROM Genre WHERE Genre_Name=%s", (name,))
        row = cursor.fetchone()

        if row:
            genre_cache[name] = row[0]
            return row[0]

        cursor.execute("INSERT INTO Genre (Genre_Name) VALUES (%s)", (name,))
        genre_id = cursor.lastrowid
        genre_cache[name] = genre_id
        return genre_id

    def get_medientyp_id(name):
        if name in medientyp_cache:
            return medientyp_cache[name]

        cursor.execute("SELECT Medientyp_ID FROM Medientypen WHERE Medientyp=%s", (name,))
        row = cursor.fetchone()

        if row:
            medientyp_cache[name] = row[0]
            return row[0]

        cursor.execute("INSERT INTO Medientypen (Medientyp) VALUES (%s)", (name,))
        medientyp_id = cursor.lastrowid
        medientyp_cache[name] = medientyp_id
        return medientyp_id

    for page in tqdm(range(1, max_pages+1), desc="Seiten"):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"

        try:
            r = session.get(url, timeout=5)
        except Exception as e:
            print(f"Fehler bei Seite {page}: {e}")
            continue

        doc = pq(r.content)

        for link in tqdm(doc("h3 > a"), desc="Bücher", leave=False):
            try:
                book_link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]

                r_book = session.get(book_link, timeout=5)
                doc_book = pq(r_book.content)

                title = doc_book("h1").text()

                genre_name = doc_book("ul.breadcrumb li:nth-child(3) a").text()
                genre_id = get_genre_id(genre_name)

                medientyp_id = get_medientyp_id("Buch")

                price_raw = doc_book(".price_color").eq(0).text()
                match = re.search(r"\d+\.\d+", price_raw)
                price = float(match.group()) if match else None

                description = doc_book("#product_description + p").text()
                description_len = len(description) if description else 0

                upc = doc_book("th:contains('UPC') + td").text()

                img_tag = doc_book(".item.active img").attr("src")
                if img_tag:
                    img_url = "https://books.toscrape.com/" + img_tag.replace("../", "")
                    try:
                        img_r = session.get(img_url, timeout=5)
                        thumbnail_size = len(img_r.content)
                    except:
                        thumbnail_size = None
                else:
                    thumbnail_size = None

                books.append((
                    title,
                    book_link,
                    genre_id,
                    medientyp_id,
                    price,
                    description_len,
                    upc,
                    thumbnail_size
                ))

            except Exception as e:
                print(f"Fehler bei Buch: {e}")
                continue

        conn.commit()

    conn.close()
    return books


# Insert into DB
def insert_books(books):
    conn = datenbank_connection()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT IGNORE INTO Artikel
        (Buchtitel, Link, Genre_ID, Medientyp_ID, Preis,
         Groesse_Beschreibung, UPC, Daten_menge_thumbnail)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, books)

    conn.commit()
    conn.close()

# Main
if __name__ == "__main__":
    create_tables()

    session = requests.Session()
    max_pages = getpages(session)

    books = scrape_books(session, max_pages=50)  # use max_pages for full scrape

    print("Anzahl Bücher:", len(books))

    df = pd.DataFrame(books, columns=[
        "Buchtitel", "Link", "Genre_ID", "Medientyp_ID",
        "Preis", "Groesse_Beschreibung", "UPC", "Daten_menge_thumbnail"
    ])

    insert_books(books)