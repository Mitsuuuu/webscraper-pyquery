import mysql.connector

def connect_to_database():
    scraper_data = mysql.connector.connect(
        host="stardrop-saloon.de:3306",
        user="root",
        password="alohomoraberlin"
 )
