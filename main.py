from Scraping import collection_loop
from Scraping import lists_to_dataframe
from database import connect_to_database

zahl = int (input("Aktion auswählen:"))
match zahl:
    case 1:
        print(collection_loop())
    case 2:
        connect_to_database()









