from sqlalchemy import create_engine

def connect_to_database():
        user="root"
        password = "alohomoraberlin"
        host = "stardrop-saloon.de"
        port = 3306
        database = "WebscrapingDB"

        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')
        return engine
