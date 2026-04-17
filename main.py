# Import required libraries
from tqdm import tqdm  # progress bars
import requests  # HTTP requests
from pyquery import PyQuery as pq  # HTML parsing
import mysql.connector  # MySQL connection
import pandas as pd  # data handling
import re  # regex for text processing

# Show full text in pandas columns
pd.set_option("display.max_colwidth", None)


# Create a connection to the MySQL database
def datenbank_connection():
    return mysql.connector.connect(
        host="stardrop-saloon.de",
        port=3306,
        user="root",
        password="alohomoraberlin",
        database="WebscrapingDB"
    )


# Create necessary tables if they do not exist
def create_tables():
    conn = datenbank_connection()
    cursor = conn.cursor()

    # Table for genres
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Genre (
            Genre_ID INT AUTO_INCREMENT PRIMARY KEY,
            Genre_Name VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Table for media types (e.g., book)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Medientypen (
            Medientyp_ID INT AUTO_INCREMENT PRIMARY KEY,
            Medientyp VARCHAR(50) NOT NULL UNIQUE
        );
    """)

    # Main table for storing book data
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


# Get total number of pages from the website
def getpages(session):
    r = session.get("https://books.toscrape.com/index.html", timeout=5)
    doc = pq(r.content)

    # Extract text like "Page 1 of 50"
    text = doc("li.current").text()

    # Return total number of pages
    return int(text.split(" of ")[1])


# Scrape book data from the website
def scrape_books(session, max_pages=2):
    books = []

    # Connect to database
    conn = datenbank_connection()
    cursor = conn.cursor()

    # Caches to avoid duplicate DB queries
    genre_cache = {}
    medientyp_cache = {}

    # Get or insert genre and return its ID
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

    # Get or insert media type and return its ID
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

    # Loop through all pages
    for page in tqdm(range(1, max_pages+1), desc="Seiten"):
        url = f"https://books.toscrape.com/catalogue/page-{page}.html"

        try:
            r = session.get(url, timeout=5)
        except Exception as e:
            print(f"Fehler bei Seite {page}: {e}")
            continue

        doc = pq(r.content)

        # Loop through all books on the page
        for link in tqdm(doc("h3 > a"), desc="Bücher", leave=False):
            try:
                # Build full book URL
                book_link = "https://books.toscrape.com/catalogue/" + link.attrib["href"]

                # Request book detail page
                r_book = session.get(book_link, timeout=5)
                doc_book = pq(r_book.content)

                # Extract book title
                title = doc_book("h1").text()

                # Extract genre and get its ID
                genre_name = doc_book("ul.breadcrumb li:nth-child(3) a").text()
                genre_id = get_genre_id(genre_name)

                # Set media type as "Buch"
                medientyp_id = get_medientyp_id("Buch")

                # Extract price using regex
                price_raw = doc_book(".price_color").eq(0).text()
                match = re.search(r"\d+\.\d+", price_raw)
                price = float(match.group()) if match else None

                # Extract description length (word count)
                description_text = doc_book("#product_description ~ p").text()
                words = re.findall(r"\b[\w']+\b", description_text)
                description_len = len(words)

                # Extract UPC code
                upc = doc_book("th:contains('UPC') + td").text()

                # Extract image and calculate its size in bytes
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

                # Store collected data
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

        # Save changes after each page
        conn.commit()

    conn.close()
    return books


# Insert scraped books into the database
def insert_books(books):
    conn = datenbank_connection()
    cursor = conn.cursor()

    # Insert data and ignore duplicates (same link)
    cursor.executemany("""
        INSERT IGNORE INTO Artikel
        (Buchtitel, Link, Genre_ID, Medientyp_ID, Preis,
         Groesse_Beschreibung, UPC, Daten_menge_thumbnail)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, books)

    conn.commit()
    conn.close()


# Main program execution
if __name__ == "__main__":
    # Create tables
    create_tables()

    # Start session for requests
    session = requests.Session()

    # Get number of pages
    max_pages = getpages(session)

    # Scrape books (limit to 50 pages here)
    books = scrape_books(session, max_pages=50)

    # Print number of books scraped
    print("Anzahl Bücher:", len(books))

    # Convert to pandas DataFrame
    df = pd.DataFrame(books, columns=[
        "Buchtitel", "Link", "Genre_ID", "Medientyp_ID",
        "Preis", "Groesse_Beschreibung", "UPC", "Daten_menge_thumbnail"
    ])

    # Insert data into database
    insert_books(books)