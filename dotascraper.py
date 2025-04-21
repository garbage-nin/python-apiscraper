import psycopg2
import requests
import json
import time
import os 
from dotenv import load_dotenv

load_dotenv()

def get_all_heroes():
    try:
      response = requests.get('https://www.dota2.com/datafeed/herolist?language=english')
      response.raise_for_status()
      return response.json()
    except Exception as e:
      print(f"🔴 An error occurred: {e}")
      return []

def get_all_items():
    try:
      response = requests.get('https://www.dota2.com/datafeed/itemlist?language=english')
      response.raise_for_status()
      return response.json()
    except Exception as e:
      print(f"🔴 An error occurred: {e}")
      return []
  
def get_hero_by_id(hero_id):
    try:
      response = requests.get(f'https://www.dota2.com/datafeed/herodata?language=english&hero_id={hero_id}')
      response.raise_for_status()
      return response.json()
    except Exception as e:
      print(f"🔴 An error occurred: {hero_id} {e}")
      return []

def parse_all_hero_resp():
    print(f"Fetching all heroes")
    all_heroes = get_all_heroes()
    if (len(all_heroes) == 0):
      print("No heroes found")
      return []

    heroes_id = [hero["id"] for hero in all_heroes["result"]["data"]["heroes"]]
    return heroes_id

def parse_all_item_resp():
    print(f"Fetching all items")
    all_items = get_all_items()
    if (len(all_items) == 0):
      print("No items found")
      return []

    items_id = [item["id"] for item in all_items["result"]["data"]["itemabilities"]]
    return items_id

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

def insert_heroes(hero_data):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor()
        query = "INSERT INTO heroes (data) VALUES (%s) RETURNING id;"
        cur.execute(query, (json.dumps(hero_data),))

        hero_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted hero with ID: {hero_id}")
        return hero_id
    except Exception as e:
        print(f"🔴 An error occurred inserting: {hero_id}")
        return []

def get_item_by_id(item_id):
    try:
      response = requests.get(f'https://www.dota2.com/datafeed/itemdata?language=english&item_id={item_id}')
      response.raise_for_status()
      return response.json()
    except Exception as e:
      print(f"🔴 An error occurred: {item_id} {e}")
      return []

def insert_items(item_data):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor()
        query = "INSERT INTO items (data) VALUES (%s) RETURNING id;"
        cur.execute(query, (json.dumps(item_data),))

        item_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted items with ID: {item_id}")
        return item_id
    except Exception as e:
        print(f"🔴 An error occurred inserting: {item_id}")
        return []

def process_heroes_to_db():
      all_heroes_id = parse_all_hero_resp()
      print (f"Heroes ID: {len(all_heroes_id)}")

      if len(all_heroes_id) == 0:
          return
      
      for hero_id in all_heroes_id:
          print(f"Fetching hero with ID: {hero_id}")
          hero_data = get_hero_by_id(hero_id)

          if len(hero_data) == 0:
              print (f"Hero with ID {hero_id} not found")
          else:
            insert_heroes(hero_data["result"]["data"]["heroes"][0])

          time.sleep(5)
    
      print("Finished processing heroes")

def process_items_to_db():
      all_items_id = sorted(parse_all_item_resp())
      print (f"Items ID: {len(all_items_id)}")

      if len(all_items_id) == 0:
          return
      
      for item_id in all_items_id:
          print(f"Fetching item with ID: {item_id}")
          item_data = get_item_by_id(item_id)
          if len(item_data) == 0:
              print (f"Item with ID {item_id} not found")
          else:
            insert_items(item_data["result"]["data"]["items"][0])

          time.sleep(3)
    
      print("Finished processing items")

def get_all_heroes_from_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor()
        query = "SELECT * FROM heroes;"
        cur.execute(query)
        heroes = cur.fetchall()
        cur.close()
        conn.close()
        return heroes
    except Exception as e:
        print(f"🔴 An error occurred: {e}")
        return []

def process_hero_images():
    heroes = get_all_heroes_from_db()
    if len(heroes) == 0:
        print("No heroes found")
        return
  
    heroes_name = [row[1]['name'].replace("npc_dota_hero_", "") for row in heroes]

    for hero_name in heroes_name:
        print(f"Downloading image for hero: {hero_name}")
        download_hero_image(hero_name)
        time.sleep(10)
    
    print("Finished downloading images")

def download_hero_image(hero_name):
    filename = f"{hero_name}.png"
    folder = "./images"
    try:
        response = requests.get(f'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/heroes/{hero_name}.png', stream=True)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)

        # Ensure the folder exists
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, filename)
        
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):  # Download in chunks
                file.write(chunk)

        print(f"Image saved to {file_path}")
        return True
    except Exception as e:
        print(f"🔴 An error occurred: {hero_name} {e}")
        return False


if __name__ == "__main__":
  #process_heroes_to_db()
  process_items_to_db()
  #process_hero_images()
  #process_hero_images()

