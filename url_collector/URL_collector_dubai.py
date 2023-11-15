import requests
from bs4 import BeautifulSoup
import os

dubai_list = {
    'https://deliveroo.ae/restaurants/dubai/deira/?geohash=thrrg1fgbqdf&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/al-khawaneej-east/?geohash=thrrx17z8984&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/nadd-al-hamar/?geohash=thrrk7e51mpd&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/dubai-international-city/?geohash=thrrhv5hj7un&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/damac-hills/?geohash=thrq3k3vg5ft&collection=all-restaurants'
'https://deliveroo.ae/restaurants/dubai/the-villa/?geohash=thrqez0fmk08&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/jumeirah-village-circle/?geohash=thrq8644pp7k&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/dubai-investment-park-1/?geohash=thrnpe6155ek&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/jebel-ali-industrial/?geohash=thrnnr46tf8j&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/discovery-gardens/?geohash=thrnqy4yzd1d&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/marina/?geohash=thrnwtzbxpgm&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/tecom/?geohash=thrnz8g07kb9&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/al-quoz-1/?geohash=thrqbzwkf8md&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/al-safa-1/?geohash=thrr1pb3559m&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/al-safa-2/?geohash=thrr0evr9432&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/jumeirah-2/?geohash=thrr35u65y9p&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/difc/?geohash=thrr3v5s0hqs&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/jafilia/?geohash=thrr9gms2953&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/karama/?geohash=thrrdp5vx2vg&collection=all-restaurants',
'https://deliveroo.ae/restaurants/sharjah/sharjah-nahda-park/?geohash=thrrun59bn0z&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/al-mizhar/?geohash=thrrtu7rj81t&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/al-qusais-3/?geohash=thrrsmth1gnf&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/mirdif/?geohash=thrrmj9wnzpc&collection=all-restaurants',
'https://deliveroo.ae/restaurants/dubai/dubai-warsan-1/?geohash=thrrjsg757ws&collection=all-restaurants',
}

class URLCollector:

    def __init__(self, city_list):
        self.__list = city_list
        self.__dir = './data'
        self.__failed_links = []

    def create_directory(self):
        if not os.path.exists(self.__dir):
            os.makedirs(self.__dir)
        self.collect_urls()
        self.log_failed_links()

    def collect_urls(self):
        all_urls = []
        for link in self.__list:
            try:
                reqs = requests.get(link)
                soup = BeautifulSoup(reqs.text, 'html.parser')

                for a_tag in soup.find_all('a'):
                    href = a_tag.get('href')
                    if href and href.startswith('/menu/'):
                        modified_href = 'https://deliveroo.ae' + href
                        all_urls.append(modified_href)
            except Exception as e:
                print(f"Failed to process {link}: {e}")
                self.__failed_links.append(link)

        # Write all URLs to a single file
        with open(os.path.join(self.__dir, "dubai_rest_links_deliveroo.txt"), "w") as f:
            for url in all_urls:
                f.write(url + "\n")

    def log_failed_links(self):
        if self.__failed_links:
            with open(os.path.join(self.__dir, "failed_links.txt"), "w") as f:
                for link in self.__failed_links:
                    f.write(link + "\n")

# Usage
url_collector = URLCollector(dubai_list)
url_collector.create_directory()