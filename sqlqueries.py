import mysql.connector
from Scraping import lists_to_dataframe
from database import connect_to_database


def import_lists_to_database():

    df_books, df_mediatype, df_genre = lists_to_dataframe()
    engine = connect_to_database()
    df_books.to_sql("Artikel", engine, if_exists='replace', index=False)