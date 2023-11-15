import inspect
import json
import sqlite3
import logging
import os.path as path
from json import loads
from os import makedirs
from pathlib import Path
import validators
from bs4 import BeautifulSoup
from pandas import DataFrame, read_csv, concat
from requests import get, HTTPError

# Setup logging
logging.basicConfig(format="%(asctime)s - [%(levelname)s]\t%(message)s",
                    datefmt='%d-%b-%y %H:%M:%S')

class DeliverooScraper:
    def __init__(self, url: str, base_dir: str = 'crawled_data',
                 f_name: str = 'crawled_data', menu_dir: str = 'menus'):
        self.url = url
        self.__details_json = None
        self.__bs4_data = None

        self.__restaurant_details = {}
        self.__restaurant_menu_details = []

        # Improved path handling
        self.__base_dir = Path(base_dir).resolve()
        self.__menu_dir = self.__base_dir / menu_dir
        self.__filename = f_name

        # Simplified URL validation and data fetching
        if not self.url_validator(url):
            logging.error(f"'{url}' is not a valid URL")
            return

        self.__bs4_data = self.fetch_details(url)
        if self.__bs4_data:
            self.__details_json = self.make_json(self.__bs4_data)
            if self.__details_json:
                self.fetch_restaurant_details(self.__details_json)
                self.fetch_restaurant_location(self.__details_json)  # Ensure this is called
                self.__restaurant_menu_details = self.extract_menu_items(self.__details_json)  # Extract menu items here


    @staticmethod
    def url_validator(link: str) -> bool:
        return validators.url(link) and link.startswith('https://deliveroo.ae/')

    @staticmethod
    def fetch_details(url):
        try:
            raw = get(url, allow_redirects=True, headers=(
                {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                  '(KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
                }
            ))

            status_code = raw.status_code
            reason = raw.reason

            if status_code != 200:
                raise HTTPError(status_code, reason)

            bs4_data = BeautifulSoup(raw.content, 'lxml')
            return bs4_data

        except HTTPError as e:
            logging.error(f"{url} - {e.strerror} [{e.errno}]")
            return None

        except Exception as e:
            logging.debug(e)
            return None

    def make_json(self, bs4_data):
        try:
            data = bs4_data.select('#__NEXT_DATA__')[0].text
            details_json = loads(data)
            return details_json

        except Exception as e:
            logging.error(e)
            return None

    def fetch_restaurant_details(self, details_json):
        try:
            restaurant = details_json['props']['initialState']['menuPage']['menu']['meta']['restaurant']
            self.__restaurant_details['name'] = restaurant.get('name', 'Unknown Name').lower().replace(" ", "_")
            self.__restaurant_details['address'] = restaurant.get('location', {}).get('address', {}).get('address1', 'Unknown Address')
            self.__restaurant_details['neighborhood'] = restaurant.get('location', {}).get('address', {}).get('neighborhood', 'Unknown Neighborhood')
        except KeyError as e:
            logging.error(f"Key error while fetching restaurant details: {e}")
        except Exception as e:
            logging.error(f"Error in fetch_restaurant_details: {e}")

    def fetch_restaurant_details(self, details_json):
        try:
            restaurant = details_json['props']['initialState']['menuPage']['menu']['meta']['restaurant']
            self.__restaurant_details['name'] = restaurant.get('name', 'Unknown Name').lower().replace(" ", "_")
            self.__restaurant_details['address'] = restaurant.get('location', {}).get('address', {}).get('address1', 'Unknown Address')
            self.__restaurant_details['neighborhood'] = restaurant.get('location', {}).get('address', {}).get('neighborhood', 'Unknown Neighborhood')
        except KeyError as e:
            logging.error(f"Key error while fetching restaurant details: {e}")
            self.__restaurant_details['name'] = 'Unknown Name'
            self.__restaurant_details['address'] = 'Unknown Address'
            self.__restaurant_details['neighborhood'] = 'Unknown Neighborhood'
        except Exception as e:
            logging.error(f"Error in fetch_restaurant_details: {e}")

    def extract_menu_items(self, details_json):
        menu_items = details_json['props']['initialState']['menuPage']['menu']['meta']['items']
        menu_data = []

        for item in menu_items:
            try:
                name = item.get('name', 'No Name')
                description = item.get('description', 'No Description')
                price = item.get('price', {}).get('formatted', 'No Price').replace('AED\xa0', '')
                image_data = item.get('image')
                image_url = image_data.get('url') if image_data else 'No Image URL'

                menu_data.append({
                    'name': name,
                    'description': description,
                    'price': price,
                    'image_url': image_url    
                })
            except KeyError as e:
                logging.error(f"Key error while fetching menu item: {e}")
                continue  # Skip this item and continue with the next
            except Exception as e:
                logging.error(f"Error in extract_menu_items: {e}")
                continue  # Skip this item and continue with the next

        return menu_data
        return menu_data
    
    def save_to_db(self, db_name: str):
        # Create or connect to a SQLite database
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        # Create tables if they don't exist
        c.execute('''CREATE TABLE IF NOT EXISTS restaurant (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        address TEXT,
                        neighborhood TEXT,
                        lat REAL,
                        lon REAL,
                        city TEXT,
                        postcode TEXT,
                        cityId INTEGER,
                        zoneId INTEGER,
                        geohash TEXT
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS menu (
                        id INTEGER PRIMARY KEY,
                        restaurant_id INTEGER,
                        name TEXT,
                        description TEXT,
                        price TEXT,
                        image_url TEXT,
                        FOREIGN KEY (restaurant_id) REFERENCES restaurant (id)
                    )''')
        
        # Update the restaurant details insertion query
        c.execute('''INSERT INTO restaurant 
                     (name, address, neighborhood, lat, lon, city, postcode, cityId, zoneId, geohash) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (self.__restaurant_details['name'], self.__restaurant_details['address'],
                   self.__restaurant_details['neighborhood'], self.__restaurant_details['lat'],
                   self.__restaurant_details['lon'], self.__restaurant_details['city'],
                   self.__restaurant_details['postcode'], self.__restaurant_details['cityId'],
                   self.__restaurant_details['zoneId'], self.__restaurant_details['geohash']))
        restaurant_id = c.lastrowid

        # Insert menu items
        for item in self.__restaurant_menu_details:
            c.execute('INSERT INTO menu (restaurant_id, name, description, price, image_url) VALUES (?, ?, ?, ?, ?)',
                        (restaurant_id, item['name'], item['description'], item['price'], item['image_url']))

        # Commit and close
        conn.commit()
        conn.close()


# Function to read URLs from a file
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to scrape URLs
def scrape_urls(file_path, db_name):
    urls = read_urls_from_file(file_path)
    failed_urls = []

    for url in urls:
        try:
            # Replace '=ASAP' with '=anytime' in the URL
            url = url.replace('=ASAP', '=anytime')

            scraper = DeliverooScraper(url)
            scraper.save_to_db(db_name)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            failed_urls.append(url)

    # Optionally, save the failed URLs to a file or handle them as needed
    with open('failed_urls_2.txt', 'w') as file:
        for url in failed_urls:
            file.write(url + '\n')

# Example usage
input_file = "failed_urls.txt"  # Path to the file containing URLs
scrape_urls(input_file, "deliveroo_dubai_27614failed.db")

# Example usage
#url = "https://deliveroo.ae/menu/Dubai/dubai-creek/kutsara-at-tinidor?day=today&geohash=thrrg50szgc9&time=anytime"
