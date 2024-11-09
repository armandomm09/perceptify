import psycopg2
from .config import load_db_config

def connect_db(config):
    
    try:
        with psycopg2.connect(**config) as conn:
            print("Connected to PostgreSQL")
            return conn
    except(psycopg2.DatabaseError, Exception) as error:
        print(error)
        

