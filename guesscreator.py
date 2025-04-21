import psycopg2
import requests
import json
import time
import os 
from dotenv import load_dotenv

load_dotenv()

def check_db_connection():
    print(os.getenv("DB_NAME"))
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        print("✅ Database connected")
    except Exception as e:
        print(f"🔴 An error occurred: {e}"
        )

def get_random_hero_from_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor()
        query = "SELECT * FROM heroes ORDER BY RANDOM() LIMIT 1;"
        cur.execute(query)
        hero = cur.fetchone()
        cur.close()
        conn.close()
        return hero
    except Exception as e:
        print(f"🔴 An error occurred: {e}")
        return []
def process_create_guess():
    hero = get_random_hero_from_db()
    print(f"Processing hero: {hero}")
    
    time.sleep(1)
    print("Guess created")


if __name__ == "__main__":
  process_create_guess()