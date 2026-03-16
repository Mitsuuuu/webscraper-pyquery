from tqdm import tqdm
import requests
from pyquery import PyQuery as pq
import mysql.connector
import pandas as pd

pd.set_option("display.max_colwidth", None)

# DB connection
def datenbank_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3307,          # Docker-Port
        user="root",        # Root-User
        password="",        # Root-Passwort
        database="WebscrapingDB"
    )


# Create tables
def create_tables():
    conn = datenbank_connection()
    cursor = conn.cursor()

    # Genre table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Genre (
            Genre_ID INT AUTO_INCREMENT PRIMARY KEY,
            Genre_Name VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Medientypen table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Medientypen (
            Medientyp_ID INT AUTO_INCREMENT PRIMARY KEY,
            Medientyp VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Artikel table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Artikel (
            Artikel_ID INT AUTO_INCREMENT PRIMARY KEY,
            Genre_ID INT NULL,
            Medientyp_ID INT NULL,
            Preis FLOAT,
            Groesse_Beschreibung INT,
            UPC VARCHAR(50),
            Daten_menge_thumbnail INT,
            Buchtitel VARCHAR(200),
            Link VARCHAR(300),
            CONSTRAINT fk_genre
                FOREIGN KEY (Genre_ID)
                REFERENCES Genre(Genre_ID)
                ON DELETE SET NULL
                ON UPDATE CASCADE,
            CONSTRAINT fk_medientyp
                FOREIGN KEY (Medientyp_ID)
                REFERENCES Medientypen(Medientyp_ID)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    print("Tabellen erstellt.")

# Number of pages
def getpages():
    r = requests.get("https://books.toscrape.com/index.html")
    doc = pq(r.content)
    text = doc("li.current").text()  # "Page 1 of 50"
    pages = text.split(" of ")
    return int(pages[1])


# Helper: Insert/get genre
def get_genre_id(genre_name):
    conn = datenbank_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Genre_ID FROM Genre WHERE Genre_Name=%s", (genre_name,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]
    cursor.execute("INSERT INTO Genre (Genre_Name) VALUES (%s)", (genre_name,))
    conn.commit()
    genre_id = cursor.lastrowid
    conn.close()
    return genre_id


# Helper: Insert/get medientyp
def get_medientyp_id(medientyp_name):
    conn = datenbank_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Medientyp_ID FROM Medientypen WHERE Medientyp=%s", (medientyp_name,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row[0]
    cursor.execute("INSERT INTO Medientypen (Medientyp) VALUES (%s)", (medientyp_name,))
    conn.commit()
    medientyp_id = cursor.lastrowid
    conn.close()
    return medientyp_id

# Scrape books
def scrape_books(max_pages=2):
    books = []

    for page in tqdm(range(1, 2), desc="Seiten"):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"
        r = requests.get(url)
        doc = pq(r.content)

        for link in tqdm(doc("h3 > a"), desc="Bücher", leave=False):
            book_link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]
            r_book = requests.get(book_link)
            doc_book = pq(r_book.content)

            # Title
            title = doc_book("h1").text()

            # Genre (breadcrumb)
            genre_name = doc_book("ul.breadcrumb li:nth-child(3) a").text()
            genre_id = get_genre_id(genre_name) if genre_name else None

            # Medientyp (Books only, so 'Buch')
            medientyp_name = "Buch"
            medientyp_id = get_medientyp_id(medientyp_name)

            # Price
            price_text = doc_book(".price_color").text().replace("£", "")
            try:
                price = float(price_text)
            except:
                price = None

            # Description length
            description = doc_book("#product_description + p").text()
            description_len = len(description) if description else 0

            # UPC
            upc = doc_book("th:contains('UPC') + td").text()

            # Thumbnail size in bytes
            img_url = "https://books.toscrape.com/" + doc_book(".item.active img").attr("src").replace("../", "")
            try:
                img_r = requests.get(img_url)
                thumbnail_size = len(img_r.content)
            except:
                thumbnail_size = None

            books.append({
                "Buchtitel": title,
                "Link": book_link,
                "Genre_ID": genre_id,
                "Medientyp_ID": medientyp_id,
                "Preis": price,
                "Groesse_Beschreibung": description_len,
                "UPC": upc,
                "Daten_menge_thumbnail": thumbnail_size
            })

    return books

# Insert into DB
def insert_books(books):
    conn = datenbank_connection()
    cursor = conn.cursor()

    for b in books:
        cursor.execute("""
            INSERT INTO Artikel
            (Buchtitel, Link, Genre_ID, Medientyp_ID, Preis, Groesse_Beschreibung, UPC, Daten_menge_thumbnail)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            b.get("Buchtitel"),
            b.get("Link"),
            b.get("Genre_ID"),
            b.get("Medientyp_ID"),
            b.get("Preis"),
            b.get("Groesse_Beschreibung"),
            b.get("UPC"),
            b.get("Daten_menge_thumbnail")
        ))

    conn.commit()
    conn.close()
    print(f"{len(books)} Bücher in die DB eingefügt.")

# Main
if __name__ == "__main__":
    create_tables()

    max_pages = getpages()  # Total pages
    books = scrape_books(max_pages=2)  # Limit to 2 for testing

    df = pd.DataFrame(books)
    print(df.head())

    insert_books(books)