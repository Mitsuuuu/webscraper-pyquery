import mysql.connector

def connect_to_database():
    scraper_data = mysql.connector.connect(
        host="stardrop-saloon.de:8080",
        user="root",
        password="alohomoraberlin"
 )
