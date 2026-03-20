from Scraping import collection_loop
from Scraping import lists_to_dataframe
from database import connect_to_database
from sqlqueries import import_lists_to_database

zahl = int (input("Aktion auswählen:"))
match zahl:
    case 1:
        import_lists_to_database()











